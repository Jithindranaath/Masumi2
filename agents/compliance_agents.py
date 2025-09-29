from crewai import Agent
import PyPDF2
import os

class ExtractorAgent(Agent):
    def parse_document(self, file):
        # If it's a file path, read the PDF
        if isinstance(file, str) and file.endswith('.pdf') and os.path.exists(file):
            try:
                with open(file, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    for page in reader.pages:  # Read all pages
                        text += page.extract_text() + "\n"
                    return text
            except Exception as e:
                return f"Error reading PDF: {str(e)}"
        else:
            # For text input, return as-is
            return f"Extracted text: {file}"


class MatcherAgent(Agent):
    def match_rules(self, text, jurisdiction):
        # Define building construction requirements for each jurisdiction
        building_requirements = {
            "India": {
                "keywords": ["building permit", "noc", "fire safety", "structural design", "environmental clearance", "municipal approval", "architect", "engineer", "foundation", "construction plan", "building code", "setback", "fsi", "far"],
                "required_docs": [
                    "Building Permit/Sanction Plan",
                    "NOC from Fire Department", 
                    "Structural Design Certificate",
                    "Environmental Clearance",
                    "Municipal Corporation Approval",
                    "Architect/Engineer License",
                    "Site Plan with Setbacks",
                    "FSI/FAR Compliance Certificate"
                ]
            },
            "EU": {
                "keywords": ["building permit", "planning permission", "structural engineer", "energy certificate", "fire safety", "accessibility", "environmental impact", "building regulations", "construction standards", "architect license"],
                "required_docs": [
                    "Building Permit",
                    "Planning Permission", 
                    "Structural Engineer Certificate",
                    "Energy Performance Certificate",
                    "Fire Safety Compliance",
                    "Accessibility Standards Compliance",
                    "Environmental Impact Assessment"
                ]
            },
            "UK": {
                "keywords": ["planning permission", "building regulations", "structural engineer", "fire safety", "building control", "architect", "construction standards", "party wall", "environmental assessment", "drainage"],
                "required_docs": [
                    "Planning Permission",
                    "Building Regulations Approval",
                    "Structural Engineer Certificate", 
                    "Fire Safety Certificate",
                    "Building Control Approval",
                    "Party Wall Agreement (if applicable)",
                    "Drainage and Utilities Plan"
                ]
            }
        }
        
        # Get requirements for jurisdiction
        requirements = building_requirements.get(jurisdiction, {"keywords": [], "required_docs": []})
        keywords = requirements["keywords"]
        required_docs = requirements["required_docs"]
        
        # Analyze text for building construction content
        text_lower = text.lower()
        found_docs = []
        missing_docs = []
        keyword_count = 0
        
        # Count keyword matches and identify found documents
        for keyword in keywords:
            if keyword in text_lower:
                keyword_count += 1
        
        # Check which required documents are mentioned
        for doc in required_docs:
            doc_keywords = doc.lower().split()
            if any(keyword in text_lower for keyword in doc_keywords):
                found_docs.append(doc)
            else:
                missing_docs.append(doc)
        
        # Calculate compliance score
        total_docs = len(required_docs)
        found_count = len(found_docs)
        compliance_score = (found_count / total_docs) if total_docs > 0 else 0
        
        # Only proceed if most requirements are met
        should_continue = compliance_score >= 0.8  # 80% of documents found
        
        return {
            "found_documents": found_docs,
            "missing_documents": missing_docs,
            "compliance_score": compliance_score,
            "should_continue": should_continue,
            "keywords_found": keyword_count,
            "total_required": total_docs,
            "analysis": f"Found {found_count}/{total_docs} required construction documents"
        }


class SummarizerAgent(Agent):
    def summarize(self, matches):
        score = matches.get('compliance_score', 0)
        found_docs = matches.get('found_documents', [])
        missing_docs = matches.get('missing_documents', [])
        total_required = matches.get('total_required', 0)
        analysis = matches.get('analysis', '')
        
        if score >= 0.8:
            status = "[APPROVED] YOU CAN PROCEED WITH CONSTRUCTION"
            recommendation = "All major construction requirements are satisfied."
        else:
            status = "[NOT APPROVED] MISSING REQUIRED DOCUMENTS"
            recommendation = "You need to obtain the missing documents before construction."
        
        summary = f"""BUILDING CONSTRUCTION COMPLIANCE REPORT
        
        STATUS: {status}
        Compliance Score: {score:.1%} ({len(found_docs)}/{total_required} documents)
        
        DOCUMENTS FOUND:
        {chr(10).join([f'  - {doc}' for doc in found_docs]) if found_docs else '  - None found'}
        
        MISSING DOCUMENTS:
        {chr(10).join([f'  - {doc}' for doc in missing_docs]) if missing_docs else '  - None missing'}
        
        ANALYSIS: {analysis}
        
        RECOMMENDATION: {recommendation}
        
        NEXT STEPS:
        {'  - Proceed with construction as all requirements are met!' if score >= 0.8 else '  - Obtain the missing documents listed above'}
        {'  - Contact local building authority for final approval' if score >= 0.8 else '  - Submit complete documentation for approval'}
        {'  - Begin construction with proper permits' if score >= 0.8 else '  - Do not start construction until all documents are obtained'}
        """
        return summary