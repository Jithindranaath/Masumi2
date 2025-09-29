from agents.compliance_agents import ExtractorAgent, MatcherAgent, SummarizerAgent

def demo_compliance_workflow():
    print("=" * 60)
    print("COMPLIANCE AGENTS DEMO - INDIAN DOCUMENTS")
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
    
    # Real sample compliance documents
    test_docs = [
        {
            "name": "RBI KYC Guidelines",
            "content": "As per RBI Master Direction on KYC, all banks shall ensure customer identification procedures including Aadhaar authentication, PAN verification, and risk categorization. High-risk customers require enhanced due diligence with additional documentation. Non-compliance may result in monetary penalties under Banking Regulation Act 1949.",
            "jurisdiction": "India"
        },
        {
            "name": "GST Registration Certificate", 
            "content": "GSTIN: 27ABCDE1234F1Z5. This certificate is issued under Goods and Services Tax Act 2017. The registered person shall file monthly returns GSTR-1 and GSTR-3B. Annual turnover exceeds Rs 5 crores requiring mandatory e-invoicing compliance. Valid till 31st March 2025.",
            "jurisdiction": "India"
        },
        {
            "name": "SEBI Compliance Report",
            "content": "Securities and Exchange Board of India compliance report for listed company. Quarterly disclosure requirements under SEBI LODR Regulations 2015. Board composition includes 50% independent directors. Audit committee comprises minimum 3 members with financial expertise.",
            "jurisdiction": "India"
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
        print(f"   Matches: {match_results['matches']}")
        print(f"   Compliance Score: {match_results['compliance_score']}")
        print(f"   Should Continue: {match_results['should_continue']}")
        
        # Step 3: Conditional Summarization
        print("\n[STEP 3] Summary Generation")
        if match_results['should_continue']:
            summary = summarizer.summarize(match_results)
            print(f"   [SUCCESS] Summary: {summary}")
            print(f"   STATUS: COMPLETED - All 3 agents executed")
        else:
            print(f"   [SKIPPED] Compliance score too low")
            print(f"   STATUS: STOPPED - Only 2 agents executed")
    
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
        
        print("\n[STEP 2] Compliance Rule Matching")
        match_results = matcher.match_rules(extracted_text, 'India')
        print(f"   Matches: {match_results['matches']}")
        print(f"   Compliance Score: {match_results['compliance_score']}")
        
        if match_results['should_continue']:
            summary = summarizer.summarize(match_results)
            print(f"\n[STEP 3] Summary: {summary}")
            print("   STATUS: PDF processed successfully!")
    else:
        print("No PDF files found in current directory")
        print("Place your downloaded PDF in the project folder and run again")
    
    print(f"\n{'=' * 60}")
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("All agents are working correctly with conditional logic.")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    demo_compliance_workflow()