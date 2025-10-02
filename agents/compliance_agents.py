from crewai import Agent
import PyPDF2
import os
import litellm
import json
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

    def _run(self, text: str, jurisdiction: str = "EU", project_type: str = "general") -> str:
        """Analyze Web3 compliance using OpenAI"""
        try:
            # Create prompt for OpenAI to analyze Web3 compliance
            prompt = f"""
            You are a Web3 regulatory compliance expert. Analyze the following {project_type} project document for {jurisdiction} Web3/crypto regulatory requirements.

            DOCUMENT TO ANALYZE:
            {text}

            Please identify:
            1. Which regulatory compliance requirements for {jurisdiction} {project_type} projects are addressed in the document
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
            if jurisdiction.upper() in ["EU", "EUROPEAN UNION"]:
                prompt += """
                - Entity Registration & Licensing / Oversight: Crypto-asset Service Providers (CASPs) must seek authorization from National Competent Authority under MiCA
                - Token Issuance / White Paper / Disclosure: Publish white paper describing risks, features, governance, disclosures under MiCA
                - KYC / Customer Due Diligence: Follow AML / KYC obligations; identify and verify customers
                - AML / CFT / Financial Crime Compliance: Comply with AML Directives (AMLD5 / AMLD6) and integrate Travel Rule
                - Consumer Protection / Disclosures / Complaints: Obligations for transparency, risk warnings, client asset segregation, complaint resolution
                - Data Protection & Privacy: Comply with GDPR: data subject rights, privacy by design, lawful basis, breach notifications
                - Operational Security / Audits / Technical Risk: Adopt operational resilience standards; security and system integrity
                - Cross-border / International Compliance: MiCA and AML rules for cross-border services
                - Taxation / Reporting / Accounting: EU / member states tax regimes; CARF (Crypto-Asset Reporting Framework)
                - Enforcement, Penalties & Legal Risk: Regulatory sanctions, bans, fines by national authorities
                - Governance / Internal Controls / Compliance Officer: Meet fit & proper criteria, governance arrangements, risk committees
                - Monitoring Regulatory Changes & Transition / Grandfathering: Grandfathering clauses during MiCA transitional periods
                """
            elif jurisdiction.upper() in ["US", "UNITED STATES"]:
                prompt += """
                - Entity Registration & Licensing / Oversight: SEC registration or exemptions; money transmitter licenses (FinCEN / states)
                - Token Issuance / White Paper / Disclosure: Comply with securities laws (prospectus, disclosures); Howey test / SEC guidance
                - KYC / Customer Due Diligence: Customer Due Diligence (CDD) norms under BSA / FinCEN
                - AML / CFT / Financial Crime Compliance: BSA / FinCEN reporting, suspicious activity reporting, sanctions screening
                - Consumer Protection / Disclosures / Complaints: Fiduciary duties, prospectus / risk disclosure obligations
                - Data Protection & Privacy: Various privacy laws (federal and state, e.g. CCPA, sectoral)
                - Operational Security / Audits / Technical Risk: SEC, CFTC, investors expectations; audit trails, cyber risk management
                - Cross-border / International Compliance: Follow US rules + foreign regime considerations for non-US users
                - Taxation / Reporting / Accounting: IRS treats crypto as property; capital gains / income tax; reporting
                - Enforcement, Penalties & Legal Risk: SEC enforcement, civil / criminal liability
                - Governance / Internal Controls / Compliance Officer: Board oversight, compliance culture, internal controls
                - Monitoring Regulatory Changes & Transition / Grandfathering: Ongoing legislative proposals (e.g. digital asset bills)
                """
            elif jurisdiction.upper() in ["UK", "UNITED KINGDOM"]:
                prompt += """
                - Entity Registration & Licensing / Oversight: Register under AML / money laundering regulatory regime (Money Laundering Regulations)
                - Token Issuance / White Paper / Disclosure: Admission / disclosures rules for regulated tokens (e.g. stablecoins)
                - KYC / Customer Due Diligence: KYC / CDD / EDD under Money Laundering Regulations
                - AML / CFT / Financial Crime Compliance: UK AML / CTF rules and Travel Rule for crypto transfers
                - Consumer Protection / Disclosures / Complaints: Financial promotion rules; fair, clear, not misleading marketing
                - Data Protection & Privacy: UK GDPR / Data Protection Act; user consent, data portability
                - Operational Security / Audits / Technical Risk: FCA expects robust systems, resilience, incident reporting
                - Cross-border / International Compliance: Manage cross-border compliance and Travel Rule obligations
                - Taxation / Reporting / Accounting: Treat crypto as capital gains / trading income; HMRC reporting
                - Enforcement, Penalties & Legal Risk: FCA enforcement (fines, prohibition), consumer complaints, legal sanctions
                - Governance / Internal Controls / Compliance Officer: Appoint compliance / MLROs, internal audit / oversight
                - Monitoring Regulatory Changes & Transition / Grandfathering: UK proposing full crypto regulatory bill; transitional phases
                """
            elif jurisdiction.upper() in ["IN", "INDIA"]:
                prompt += """
                - Entity Registration & Licensing / Oversight: Register as VASP / Reporting Entity under PMLA / FIU-IND; corporate registrations
                - Token Issuance / White Paper / Disclosure: Document token model, rights, vesting, risk factors; disclaimers, disclosures
                - KYC / Customer Due Diligence: Conduct KYC / identity verification, periodic re-verification, enhanced due diligence
                - AML / CFT / Financial Crime Compliance: Monitor transactions, detect suspicious activity (STRs), report to FIU-IND; sanctions compliance
                - Consumer Protection / Disclosures / Complaints: Clear disclosures of risk, fees, terms, user agreement, complaint mechanism
                - Data Protection & Privacy: Comply with DPDP Act: purpose limitation, consent, breach notification, data subject rights
                - Operational Security / Audits / Technical Risk: Security audits, penetration tests, key custody, incident response
                - Cross-border / International Compliance: FATF recommendations; Travel Rule for cross-border transfers; data localization
                - Taxation / Reporting / Accounting: Tax gains on Virtual Digital Assets (30% + surcharge); TDS on transactions; records for audits
                - Enforcement, Penalties & Legal Risk: Fines, prosecution under PMLA / FIU; penalties under DPDP
                - Governance / Internal Controls / Compliance Officer: Compliance officer / MLRO; internal audit, training, policies
                - Monitoring Regulatory Changes & Transition / Grandfathering: Monitor updates in DPDP rules, new crypto legislation
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

            # Add project type specific context
            if project_type.upper() in ["DEFI", "DEFI"]:
                prompt += """
                This is a DeFi project. Focus on aspects like:
                - AMM, lending, staking, yield farming protocols
                - Smart contract risks, oracle dependencies
                - Liquidity provision and impermanent loss disclosures
                - Cross-chain bridge security and audits
                - Token emission schedules and governance
                """
            elif project_type.upper() in ["NFT", "NFT"]:
                prompt += """
                This is an NFT project. Focus on aspects like:
                - Intellectual property rights and licensing
                - Marketplace obligations and royalties
                - Creator verification and provenance
                - Secondary market trading and disclosures
                - Utility vs collectible classification
                """
            elif project_type.upper() in ["DAO", "DAO"]:
                prompt += """
                This is a DAO project. Focus on aspects like:
                - Governance token classification and securities laws
                - Treasury management and multisig controls
                - Voting mechanisms and quorum requirements
                - Legal entity wrappers and liability
                - Member participation and dispute resolution
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
                "keywords": ["mica", "gdpr", "aml", "kyc", "crypto", "token", "blockchain", "defi", "dao", "nft", "compliance", "regulation", "privacy", "data protection", "travel rule", "casps"],
                "required_compliance": [
                    "Entity Registration & Licensing / Oversight",
                    "Token Issuance / White Paper / Disclosure",
                    "KYC / Customer Due Diligence",
                    "AML / CFT / Financial Crime Compliance",
                    "Consumer Protection / Disclosures / Complaints",
                    "Data Protection & Privacy",
                    "Operational Security / Audits / Technical Risk",
                    "Cross-border / International Compliance",
                    "Taxation / Reporting / Accounting",
                    "Enforcement, Penalties & Legal Risk",
                    "Governance / Internal Controls / Compliance Officer",
                    "Monitoring Regulatory Changes & Transition / Grandfathering"
                ]
            },
            "US": {
                "keywords": ["sec", "cftc", "finra", "securities", "security token", "utility token", "howey test", "registration", "compliance", "regulation", "crypto", "blockchain", "bsa", "fincen", "ccpa"],
                "required_compliance": [
                    "Entity Registration & Licensing / Oversight",
                    "Token Issuance / White Paper / Disclosure",
                    "KYC / Customer Due Diligence",
                    "AML / CFT / Financial Crime Compliance",
                    "Consumer Protection / Disclosures / Complaints",
                    "Data Protection & Privacy",
                    "Operational Security / Audits / Technical Risk",
                    "Cross-border / International Compliance",
                    "Taxation / Reporting / Accounting",
                    "Enforcement, Penalties & Legal Risk",
                    "Governance / Internal Controls / Compliance Officer",
                    "Monitoring Regulatory Changes & Transition / Grandfathering"
                ]
            },
            "UK": {
                "keywords": ["fca", "financial conduct authority", "cryptoasset", "regulation", "compliance", "aml", "kyc", "financial promotion", "consumer protection", "travel rule", "hmrc"],
                "required_compliance": [
                    "Entity Registration & Licensing / Oversight",
                    "Token Issuance / White Paper / Disclosure",
                    "KYC / Customer Due Diligence",
                    "AML / CFT / Financial Crime Compliance",
                    "Consumer Protection / Disclosures / Complaints",
                    "Data Protection & Privacy",
                    "Operational Security / Audits / Technical Risk",
                    "Cross-border / International Compliance",
                    "Taxation / Reporting / Accounting",
                    "Enforcement, Penalties & Legal Risk",
                    "Governance / Internal Controls / Compliance Officer",
                    "Monitoring Regulatory Changes & Transition / Grandfathering"
                ]
            },
            "IN": {
                "keywords": ["pmla", "fiu-ind", "dpdp", "vasp", "crypto", "token", "blockchain", "defi", "dao", "nft", "compliance", "regulation", "kyc", "aml", "fatf", "travel rule"],
                "required_compliance": [
                    "Entity Registration & Licensing / Oversight",
                    "Token Issuance / White Paper / Disclosure",
                    "KYC / Customer Due Diligence",
                    "AML / CFT / Financial Crime Compliance",
                    "Consumer Protection / Disclosures / Complaints",
                    "Data Protection & Privacy",
                    "Operational Security / Audits / Technical Risk",
                    "Cross-border / International Compliance",
                    "Taxation / Reporting / Accounting",
                    "Enforcement, Penalties & Legal Risk",
                    "Governance / Internal Controls / Compliance Officer",
                    "Monitoring Regulatory Changes & Transition / Grandfathering"
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