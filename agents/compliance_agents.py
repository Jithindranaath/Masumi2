from crewai import Agent


class ExtractorAgent(Agent):
    def parse_document(self, file):
        return "Dummy extracted text from document"


class MatcherAgent(Agent):
    def match_rules(self, text, jurisdiction):
        return {"matches": ["Rule 1", "Rule 2"], "compliance_score": 0.85}


class SummarizerAgent(Agent):
    def summarize(self, matches):
        return "Dummy compliance summary and checklist"