from crewai import Crew, Task
from logging_config import get_logger
from agents.compliance_agents import ExtractorAgent, MatcherAgent, SummarizerAgent

class ComplianceCrew:
    def __init__(self, verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.crew = self.create_crew()
        self.logger.info("ComplianceCrew initialized")

    def create_crew(self):
        self.logger.info("Creating compliance crew with agents")
        
        extractor = ExtractorAgent(
            role='Web3 Document Analyzer',
            goal='Extract and analyze content from Web3 project documents',
            backstory='Expert at parsing whitepapers, tokenomics, and Web3 documentation',
            verbose=self.verbose
        )

        matcher = MatcherAgent(
            role='Web3 Compliance Expert',
            goal='Analyze Web3 projects against regulatory requirements',
            backstory='Specialized in MiCA, SEC, FCA, and other Web3 regulatory frameworks',
            verbose=self.verbose
        )

        summarizer = SummarizerAgent(
            role='Web3 Compliance Advisor',
            goal='Provide comprehensive compliance roadmap and risk assessment',
            backstory='Expert at creating actionable compliance strategies for Web3 startups',
            verbose=self.verbose
        )

        self.logger.info("Created extractor, matcher, and summarizer agents")

        extract_task = Task(
            description='Extract text content from the {project_type} project document: {text}. Provide the raw document content for compliance analysis.',
            expected_output='Raw extracted text from the {project_type} project document',
            agent=extractor
        )

        match_task = Task(
            description='Analyze {project_type} compliance for {region} region. Document: {text}. Check against MiCA (EU), SEC regulations (US), FCA rules (UK), PMLA (IN), and other relevant frameworks. Only continue if compliance_score > 0.7',
            expected_output='{project_type} compliance analysis with regulatory requirements, risk assessment, and launch readiness for {region} jurisdiction',
            agent=matcher
        )

        summarize_task = Task(
            description='Create comprehensive {project_type} compliance roadmap from analysis results. Include compliance checklist, risk mitigation steps, and regulatory next steps for {region} jurisdiction.',
            expected_output='{project_type} compliance checklist, risk assessment, and actionable roadmap',
            agent=summarizer,
            context=[extract_task, match_task]
        )
        
        crew = Crew(
            agents=[extractor, matcher, summarizer],
            tasks=[extract_task, match_task, summarize_task]
        )
        self.logger.info("Compliance crew setup completed")
        return crew