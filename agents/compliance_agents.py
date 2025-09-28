from crewai import Agent


class ExtractorAgent(Agent):
    def parse_document(self, file):
        return "Dummy extracted text from document"


class MatcherAgent(Agent):
    def match_rules(self, text, jurisdiction):
        # Simulate rule matching with condition check
        compliance_score = 0.85
        matches = ["Rule 1", "Rule 2"]
        
        # Only proceed if compliance score > 0.7
        should_continue = compliance_score > 0.7
        
        return {
            "matches": matches, 
            "compliance_score": compliance_score,
            "should_continue": should_continue
        }


class SummarizerAgent(Agent):
    def summarize(self, matches):
        return "Dummy compliance summary and checklist"