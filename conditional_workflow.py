from agents.compliance_agents import ExtractorAgent, MatcherAgent, SummarizerAgent

class BuildingComplianceWorkflow:
    def __init__(self):
        self.extractor = ExtractorAgent(
            role='Document Parser',
            goal='Extract text from building permit documents',
            backstory='Expert at parsing construction documents'
        )
        self.matcher = MatcherAgent(
            role='Building Code Checker', 
            goal='Verify building construction requirements',
            backstory='Expert in building codes and construction regulations'
        )
        self.summarizer = SummarizerAgent(
            role='Construction Approval Agent',
            goal='Provide construction approval or missing requirements', 
            backstory='Expert at construction project approvals'
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