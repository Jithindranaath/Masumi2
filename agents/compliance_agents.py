from crewai import Agent
import PyPDF2
import os
import litellm
from dotenv import load_dotenv
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# Load environment variables
load_dotenv()

# CrewAI Tools for custom functionality
class DocumentExtractionTool(BaseTool):
    name: str = "Document Extraction Tool"
    description: str = "Extracts text content from PDF documents or text input"

    def _run(self, document_path: str) -> str:
        """Extract text from document"""
        if document_path.endswith('.pdf') and os.path.exists(document_path):
            try:
                with open(document_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except Exception as e:
                return f"Error reading PDF: {str(e)}"
        else:
            return f"Extracted text: {document_path}"

class ComplianceAnalysisTool(BaseTool):
    name: str = "Web3 Compliance Analysis Tool"
    description: str = "Analyzes Web3 project documents against regulatory compliance requirements using AI"

    def _run(self, text: str, jurisdiction: str = "EU") -> str:
        """Analyze Web3 compliance using OpenAI"""
        try:
            # Create prompt for OpenAI to analyze Web3 compliance
            prompt = f"""
            You are a Web3 regulatory compliance expert. Analyze the following project document for {jurisdiction} Web3/crypto regulatory requirements.

            DOCUMENT TO ANALYZE:
            {text}

            Please identify:
            1. Which regulatory compliance requirements for {jurisdiction} Web3 projects are addressed in the document
            2. Which compliance requirements are missing or not addressed
            3. Calculate a compliance readiness score (0-1) based on how many requirements are met
            4. Determine if the project is ready for launch (requires 70%+ compliance)
            5. Identify specific regulatory risks and concerns

            Return your analysis in the following JSON format:
            {{
                "found_compliance": ["MiCA Compliance", "GDPR Article 13"],
                "missing_compliance": ["KYC Procedures", "AML Documentation"],
                "compliance_score": 0.75,
                "ready_for_launch": true,
                "risk_level": "medium",
                "regulatory_frameworks": ["MiCA", "GDPR", "AML Directive"],
                "analysis": "Detailed analysis of regulatory compliance status"
            }}

            Consider these {jurisdiction} Web3 regulatory frameworks:
            """

            # Add jurisdiction-specific Web3 requirements to the prompt
            if jurisdiction == "EU":
                prompt += """
                - MiCA (Markets in Crypto-Assets Regulation) Compliance
                - GDPR (General Data Protection Regulation) Compliance
                - AML Directive (Anti-Money Laundering) Requirements
                - Consumer Protection Laws
                - Financial Services Regulation
                - Data Protection Impact Assessment
                - KYC/AML Procedures for Users
                - Token Classification (Security vs Utility)
                """
            elif jurisdiction == "US":
                prompt += """
                - SEC (Securities and Exchange Commission) Registration
                - CFTC (Commodity Futures Trading Commission) Compliance
                - State Money Transmitter Licenses
                - Federal Securities Laws
                - Consumer Financial Protection Bureau (CFPB) Rules
                - Bank Secrecy Act (BSA) Compliance
                - FINRA (Financial Industry Regulatory Authority) Rules
                - Howey Test Analysis for Tokens
                """
            elif jurisdiction == "UK":
                prompt += """
                - FCA (Financial Conduct Authority) Registration
                - Money Laundering Regulations 2017
                - Electronic Money Regulations 2011
                - Payment Services Regulations 2017
                - Consumer Protection Regulations
                - Financial Services and Markets Act 2000
                - Cryptoasset Promotion Rules
                """
            else:
                prompt += """
                - Securities Law Compliance
                - Anti-Money Laundering (AML) Requirements
                - Know Your Customer (KYC) Procedures
                - Consumer Protection Laws
                - Data Privacy Regulations
                - Financial Services Licensing
                """

            # Get OpenAI API key from environment
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                # Fallback to hardcoded logic if no API key
                return json.dumps(self._fallback_web3_analysis(text, jurisdiction))

            # Call OpenAI via LiteLLM
            response = litellm.completion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Web3 regulatory compliance expert specializing in crypto, DeFi, and blockchain projects. Always respond with valid JSON."},
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
                return json.dumps(result)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return json.dumps(result)
                else:
                    raise ValueError(f"Could not parse OpenAI response as JSON: {result_text}")

        except Exception as e:
            # Fallback to hardcoded logic if OpenAI fails
            return json.dumps(self._fallback_web3_analysis(text, jurisdiction))

    def _fallback_web3_analysis(self, text, jurisdiction):
        """Fallback method using hardcoded Web3 rules if OpenAI fails"""
        # Define Web3 compliance requirements for each jurisdiction
        web3_requirements = {
            "EU": {
                "keywords": ["mica", "gdpr", "aml", "kyc", "crypto", "token", "blockchain", "defi", "dao", "nft", "compliance", "regulation", "privacy", "data protection"],
                "required_compliance": [
                    "MiCA Compliance Assessment",
                    "GDPR Privacy Impact Assessment",
                    "KYC/AML Procedures",
                    "Consumer Protection Measures",
                    "Financial Crime Prevention",
                    "Data Protection Compliance",
                    "Regulatory Registration Status"
                ]
            },
            "US": {
                "keywords": ["sec", "cftc", "finra", "securities", "security token", "utility token", "howey test", "registration", "compliance", "regulation", "crypto", "blockchain"],
                "required_compliance": [
                    "SEC Registration Status",
                    "Securities Law Compliance",
                    "Money Transmitter Licenses",
                    "CFTC Registration Status",
                    "Consumer Protection Compliance",
                    "Bank Secrecy Act Compliance",
                    "State Regulatory Compliance"
                ]
            },
            "UK": {
                "keywords": ["fca", "financial conduct authority", "cryptoasset", "regulation", "compliance", "aml", "kyc", "financial promotion", "consumer protection"],
                "required_compliance": [
                    "FCA Registration Status",
                    "Money Laundering Regulations Compliance",
                    "Financial Promotion Compliance",
                    "Consumer Protection Regulations",
                    "Electronic Money Regulations",
                    "Payment Services Compliance"
                ]
            }
        }

        # Get requirements for jurisdiction
        requirements = web3_requirements.get(jurisdiction, web3_requirements["EU"])
        keywords = requirements["keywords"]
        required_compliance = requirements["required_compliance"]

        # Analyze text for Web3 compliance content
        text_lower = text.lower()
        found_compliance = []
        missing_compliance = []
        keyword_count = 0

        # Count keyword matches and identify found compliance measures
        for keyword in keywords:
            if keyword in text_lower:
                keyword_count += 1

        # Check which compliance requirements are addressed
        for compliance_item in required_compliance:
            compliance_keywords = compliance_item.lower().split()
            if any(keyword in text_lower for keyword in compliance_keywords):
                found_compliance.append(compliance_item)
            else:
                missing_compliance.append(compliance_item)

        # Calculate compliance score
        total_requirements = len(required_compliance)
        found_count = len(found_compliance)
        compliance_score = (found_count / total_requirements) if total_requirements > 0 else 0

        # Determine if ready for launch
        ready_for_launch = compliance_score >= 0.7  # 70% compliance threshold

        # Assess risk level
        if compliance_score >= 0.8:
            risk_level = "low"
        elif compliance_score >= 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"

        return {
            "found_compliance": found_compliance,
            "missing_compliance": missing_compliance,
            "compliance_score": compliance_score,
            "ready_for_launch": ready_for_launch,
            "risk_level": risk_level,
            "regulatory_frameworks": [f"{jurisdiction} Web3 Regulations"],
            "analysis": f"Found {found_count}/{total_requirements} Web3 compliance requirements. Risk level: {risk_level}"
        }

class ExtractorAgent(Agent):
    def __init__(self, **kwargs):
        # Create the document extraction tool
        extraction_tool = DocumentExtractionTool()

        super().__init__(
            tools=[extraction_tool],
            allow_delegation=False,
            llm=None,  # Disable LLM calls for pure extraction
            **kwargs
        )


class MatcherAgent(Agent):
    def __init__(self, **kwargs):
        # Create the compliance analysis tool
        analysis_tool = ComplianceAnalysisTool()

        super().__init__(
            tools=[analysis_tool],
            allow_delegation=False,
            **kwargs
        )


class SummarizerAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            allow_delegation=False,
            **kwargs
        )