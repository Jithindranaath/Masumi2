from crew_definition import ComplianceCrew
from logging_config import setup_logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test CrewAI execution directly
def test_crew_directly():
    print("Testing CrewAI execution directly...")

    # Set up logging
    logger = setup_logging()

    # Get OpenAI API key from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        print("✓ OpenAI API key loaded from environment")
    else:
        print("✗ OpenAI API key not found in environment")
        return False

    try:
        # Create compliance crew
        print("Creating ComplianceCrew...")
        crew = ComplianceCrew(logger=logger)

        # Test input
        test_input = "Building permit approved by Municipal Corporation. NOC obtained from Fire Department."

        print(f"Executing crew with input: {test_input}")
        result = crew.crew.kickoff(inputs={"text": test_input})

        print("✓ CrewAI execution successful!")
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")

        if hasattr(result, 'json_dict'):
            print(f"JSON dict: {result.json_dict}")

        return True

    except Exception as e:
        print(f"✗ CrewAI execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_crew_directly()