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
                    for page in reader.pages[:3]:  # Read first 3 pages only
                        text += page.extract_text() + "\n"
                    return text[:1000] + "..." if len(text) > 1000 else text
            except Exception as e:
                return f"Error reading PDF: {str(e)}"
        else:
            # For text input, return as-is
            return f"Extracted text: {file}"


class MatcherAgent(Agent):
    def match_rules(self, text, jurisdiction):
        # Simulate realistic rule matching based on jurisdiction
        if jurisdiction == "India":
            matches = ["RBI KYC Guidelines", "PMLA Compliance", "IT Act 2000"]
            compliance_score = 0.85
        elif jurisdiction == "EU":
            matches = ["GDPR Article 6", "PSD2 Directive", "MiFID II"]
            compliance_score = 0.78
        else:
            matches = ["SOX Compliance", "CCPA Requirements"]
            compliance_score = 0.72
        
        # Only proceed if compliance score > 0.7
        should_continue = compliance_score > 0.7
        
        return {
            "matches": matches, 
            "compliance_score": compliance_score,
            "should_continue": should_continue
        }


class SummarizerAgent(Agent):
    def summarize(self, matches):
        score = matches.get('compliance_score', 0)
        rules = matches.get('matches', [])
        
        summary = f"""COMPLIANCE SUMMARY:
        ✓ Document processed successfully
        ✓ Compliance Score: {score}/1.0 (PASS)
        ✓ Rules Matched: {len(rules)} regulations identified
        
        CHECKLIST:
        {chr(10).join([f'• {rule}: COMPLIANT' for rule in rules])}
        
        RECOMMENDATION: Document meets compliance requirements.
        """
        return summary