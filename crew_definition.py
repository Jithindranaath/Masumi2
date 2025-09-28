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
            role='Document Extractor',
            goal='Parse and extract text from uploaded documents',
            backstory='Expert at document parsing and text extraction',
            verbose=self.verbose
        )

        matcher = MatcherAgent(
            role='Compliance Matcher',
            goal='Compare extracted text with predefined compliance rules',
            backstory='Specialized in compliance rule matching and validation',
            verbose=self.verbose
        )

        summarizer = SummarizerAgent(
            role='Compliance Summarizer',
            goal='Produce final compliance checklist and summary',
            backstory='Expert at creating compliance reports and summaries',
            verbose=self.verbose
        )

        self.logger.info("Created extractor, matcher, and summarizer agents")

        crew = Crew(
            agents=[extractor, matcher, summarizer],
            tasks=[
                Task(
                    description='Extract text from document: {text}',
                    expected_output='Extracted text content from the document',
                    agent=extractor
                ),
                Task(
                    description='Match extracted content against compliance rules using dummy jurisdiction',
                    expected_output='Compliance rule matching results with scores',
                    agent=matcher
                ),
                Task(
                    description='Generate compliance summary and checklist from matching results',
                    expected_output='Final compliance checklist and summary report',
                    agent=summarizer
                )
            ]
        )
        self.logger.info("Compliance crew setup completed")
        return crew