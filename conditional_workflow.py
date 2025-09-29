from agents.compliance_agents import ExtractorAgent, MatcherAgent, SummarizerAgent

class ConditionalComplianceWorkflow:
    def __init__(self):
        self.extractor = ExtractorAgent(
            role='Document Extractor',
            goal='Parse documents',
            backstory='Expert extractor'
        )
        self.matcher = MatcherAgent(
            role='Compliance Matcher', 
            goal='Match rules',
            backstory='Expert matcher'
        )
        self.summarizer = SummarizerAgent(
            role='Compliance Summarizer',
            goal='Create summaries', 
            backstory='Expert summarizer'
        )
    
    def run_workflow(self, document, jurisdiction="EU"):
        # Step 1: Extract
        extracted_text = self.extractor.parse_document(document)
        
        # Step 2: Match with condition check
        match_results = self.matcher.match_rules(extracted_text, jurisdiction)
        
        # Step 3: Only summarize if conditions met
        if match_results.get("should_continue", False):
            summary = self.summarizer.summarize(match_results)
            return {
                "status": "completed",
                "extracted": extracted_text,
                "matches": match_results,
                "summary": summary
            }
        else:
            return {
                "status": "stopped_at_matching",
                "extracted": extracted_text,
                "matches": match_results,
                "summary": "Process stopped - Compliance conditions not met",
                "reason": "Compliance score too low"
            }