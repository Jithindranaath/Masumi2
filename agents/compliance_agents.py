from crewai import Agent
import PyPDF2
import os
import litellm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ExtractorAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            allow_delegation=False,
            **kwargs
        )

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
    def __init__(self, **kwargs):
        super().__init__(
            allow_delegation=False,
            **kwargs
        )

    def match_rules(self, text, jurisdiction):
        try:
            # Create prompt for OpenAI to analyze compliance
            prompt = f"""
            You are a building construction compliance expert. Analyze the following text for {jurisdiction} building construction requirements.

            TEXT TO ANALYZE:
            {text}

            Please identify:
            1. Which required documents for {jurisdiction} building construction are present in the text
            2. Which required documents are missing
            3. Calculate a compliance score (0-1) based on how many required documents are found
            4. Determine if construction should proceed (requires 80%+ compliance)

            Return your analysis in the following JSON format:
            {{
                "found_documents": ["Document 1", "Document 2"],
                "missing_documents": ["Document 3", "Document 4"],
                "compliance_score": 0.75,
                "should_continue": true,
                "keywords_found": 8,
                "total_required": 10,
                "analysis": "Brief explanation of findings"
            }}

            Consider these typical {jurisdiction} building construction requirements:
            """

            # Add jurisdiction-specific requirements to the prompt
            if jurisdiction == "India":
                prompt += """
                - Building Permit/Sanction Plan
                - NOC from Fire Department
                - Structural Design Certificate
                - Environmental Clearance
                - Municipal Corporation Approval
                - Architect/Engineer License
                - Site Plan with Setbacks
                - FSI/FAR Compliance Certificate
                """
            elif jurisdiction == "EU":
                prompt += """
                - Building Permit
                - Planning Permission
                - Structural Engineer Certificate
                - Energy Performance Certificate
                - Fire Safety Compliance
                - Accessibility Standards Compliance
                - Environmental Impact Assessment
                """
            elif jurisdiction == "UK":
                prompt += """
                - Planning Permission
                - Building Regulations Approval
                - Structural Engineer Certificate
                - Fire Safety Certificate
                - Building Control Approval
                - Party Wall Agreement (if applicable)
                - Drainage and Utilities Plan
                """
            else:
                prompt += """
                - Building Permit
                - Construction Approval
                - Safety Compliance Documents
                - Environmental Clearance
                """

            # Get OpenAI API key from environment
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                # Fallback to hardcoded logic if no API key
                return self._fallback_match_rules(text, jurisdiction)

            # Call OpenAI via LiteLLM
            response = litellm.completion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a building construction compliance expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                api_key=openai_api_key,
                temperature=0.1
            )

            # Parse the JSON response
            result_text = response.choices[0].message.content.strip()

            try:
                import json
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError(f"Could not parse OpenAI response as JSON: {result_text}")

            return result

        except Exception as e:
            # Fallback to hardcoded logic if OpenAI fails
            return self._fallback_match_rules(text, jurisdiction)

    def _fallback_match_rules(self, text, jurisdiction):
        """Fallback method using hardcoded rules if OpenAI fails"""
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
    def __init__(self, **kwargs):
        super().__init__(
            allow_delegation=False,
            **kwargs
        )

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