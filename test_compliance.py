from agents.compliance_agents import ExtractorAgent, MatcherAgent, SummarizerAgent

def demo_building_compliance():
    print("=" * 60)
    print("BUILDING CONSTRUCTION COMPLIANCE DEMO")
    print("=" * 60)
    
    # Initialize agents
    print("\n1. Initializing Agents...")
    extractor = ExtractorAgent(
        role='Document Extractor',
        goal='Parse documents', 
        backstory='Expert at document parsing'
    )
    matcher = MatcherAgent(
        role='Compliance Matcher',
        goal='Match compliance rules',
        backstory='Expert at rule matching'
    )
    summarizer = SummarizerAgent(
        role='Compliance Summarizer', 
        goal='Create summaries',
        backstory='Expert at summarization'
    )
    print("[SUCCESS] All agents initialized successfully")
    
    # Building construction documents for testing
    test_docs = [
        {
            "name": "Complete Indian Building Documents",
            "content": "Building permit approved by Municipal Corporation. NOC obtained from Fire Department for fire safety compliance. Structural design certified by licensed engineer. Environmental clearance granted. Architect license verified. Site plan shows proper setbacks. FSI compliance certificate issued. Foundation design approved.",
            "jurisdiction": "India"
        },
        {
            "name": "Incomplete Building Documents", 
            "content": "Building permit application submitted. Architect has prepared initial drawings. Site survey completed. Some structural calculations done. Need to obtain fire safety clearance and environmental approvals.",
            "jurisdiction": "India"
        },
        {
            "name": "UK Building Documents",
            "content": "Planning permission granted by local council. Building regulations approval obtained. Structural engineer certificate provided. Fire safety compliance verified. Building control approval issued. Party wall agreement signed with neighbors. Drainage plan approved.",
            "jurisdiction": "UK"
        }
    ]
    
    # Process each document
    for i, doc in enumerate(test_docs, 1):
        print(f"\n{'-' * 50}")
        print(f"TEST {i}: {doc['name']}")
        print(f"{'-' * 50}")
        print(f"Document: {doc['content'][:80]}...")
        print(f"Jurisdiction: {doc['jurisdiction']}")
        
        # Step 1: Extraction
        print("\n[STEP 1] Document Extraction")
        extracted_text = extractor.parse_document(doc['content'])
        print(f"   Result: {extracted_text}")
        
        # Step 2: Rule Matching
        print("\n[STEP 2] Compliance Rule Matching")
        match_results = matcher.match_rules(extracted_text, doc['jurisdiction'])
        print(f"   Found Documents: {match_results['found_documents']}")
        print(f"   Missing Documents: {match_results['missing_documents']}")
        print(f"   Compliance Score: {match_results['compliance_score']:.1%}")
        print(f"   Should Continue: {match_results['should_continue']}")
        
        # Step 3: Conditional Summarization
        print("\n[STEP 3] Summary Generation")
        if match_results['should_continue']:
            summary = summarizer.summarize(match_results)
            print(f"\n[STEP 3] Construction Approval")
            print(f"   [SUCCESS] {summary}")
            print(f"   STATUS: APPROVED - All 3 agents executed")
        else:
            print(f"\n[STEP 3] Construction Approval")
            print(f"   [REJECTED] Missing required documents")
            print(f"   STATUS: NOT APPROVED - Only 2 agents executed")
    
    # Test with actual PDF if available
    print(f"\n{'-' * 50}")
    print("PDF TEST: Testing with downloaded PDF")
    print(f"{'-' * 50}")
    
    # Look for PDF files in current directory
    import os
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if pdf_files:
        pdf_file = pdf_files[0]  # Use first PDF found
        print(f"Found PDF: {pdf_file}")
        
        print("\n[STEP 1] PDF Document Extraction")
        extracted_text = extractor.parse_document(pdf_file)
        print(f"   Result: {extracted_text[:200]}...")
        
        print("\n[STEP 2] Building Code Compliance Check")
        match_results = matcher.match_rules(extracted_text, 'India')
        print(f"   Found Documents: {match_results['found_documents']}")
        print(f"   Missing Documents: {match_results['missing_documents']}")
        print(f"   Compliance Score: {match_results['compliance_score']:.1%}")
        
        if match_results['should_continue']:
            summary = summarizer.summarize(match_results)
            print(f"\n[STEP 3] Construction Approval: APPROVED")
        else:
            print(f"\n[STEP 3] Construction Approval: NOT APPROVED - Missing documents")
    else:
        print("No PDF files found in current directory")
        print("Place your building permit PDF in the project folder and run again")
    
    print(f"\n{'=' * 60}")
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("All agents are working correctly with conditional logic.")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    demo_building_compliance()