from crew_definition import ComplianceCrew

def test_end_to_end():
    print("Starting end-to-end compliance test...")
    
    # Test input
    input_data = {
        "text": "Sample compliance document for financial services in EU jurisdiction"
    }
    
    # Initialize crew
    crew = ComplianceCrew(verbose=True)
    
    # Run the workflow
    print("\nRunning ComplianceCrew workflow...")
    result = crew.crew.kickoff(input_data)
    
    print(f"\nFinal Result: {result}")
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_end_to_end()