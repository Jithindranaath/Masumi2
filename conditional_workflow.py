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
        print(f"Step 1 - Extracted: {extracted_text}")
        
        # Step 2: Match with condition check
        match_results = self.matcher.match_rules(extracted_text, jurisdiction)
        print(f"Step 2 - Match results: {match_results}")
        
        # Step 3: Only summarize if conditions met
        if match_results.get("should_continue", False):
            summary = self.summarizer.summarize(match_results)
            print(f"Step 3 - Summary: {summary}")
            return {
                "status": "completed",
                "extracted": extracted_text,
                "matches": match_results,
                "summary": summary
            }
        else:
            print("Step 3 - Skipped: Conditions not met")
            return {
                "status": "stopped_at_matching",
                "extracted": extracted_text,
                "matches": match_results,
                "reason": "Compliance score too low"
            }