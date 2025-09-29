import requests
import json
import time

def test_compliance_pipeline():
    """Test the complete compliance pipeline with comprehensive data"""

    base_url = "http://0.0.0.0:8000"

    # Test 1: Health check
    print("=== TEST 1: Health Check ===")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✓ Health: {response.json()}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return

    # Test 2: Input schema
    print("\n=== TEST 2: Input Schema ===")
    try:
        response = requests.get(f"{base_url}/input_schema")
        print(f"✓ Schema: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"✗ Schema check failed: {e}")
        return

    # Test 3: Complete building compliance documents
    print("\n=== TEST 3: Complete Building Compliance Test ===")
    complete_docs = {
        "identifier_from_purchaser": "test_user_complete",
        "input_data": {
            "text": """Building permit approved by Municipal Corporation.
            NOC obtained from Fire Department for fire safety compliance.
            Structural design certified by licensed engineer.
            Environmental clearance granted.
            Architect license verified.
            Site plan shows proper setbacks.
            FSI compliance certificate issued.
            Foundation design approved."""
        }
    }

    try:
        print("Sending complete compliance documents...")
        response = requests.post(f"{base_url}/start_job", json=complete_docs)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✓ SUCCESS! Full response:")
            print(json.dumps(result, indent=2))

            # Check if test_mode flag is present
            if result.get("test_mode"):
                print("✓ Test mode flag present")
            else:
                print("✗ Test mode flag missing")

            # Check if result is present
            if result.get("result"):
                print("✓ Result present")
            else:
                print("✗ Result missing")

        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"Error: {response.json()}")

    except Exception as e:
        print(f"✗ Request failed: {e}")

    # Test 4: Incomplete building documents
    print("\n=== TEST 4: Incomplete Building Documents Test ===")
    incomplete_docs = {
        "identifier_from_purchaser": "test_user_incomplete",
        "input_data": {
            "text": """Building permit application submitted.
            Architect has prepared initial drawings.
            Site survey completed.
            Some structural calculations done.
            Need to obtain fire safety clearance and environmental approvals."""
        }
    }

    try:
        print("Sending incomplete compliance documents...")
        response = requests.post(f"{base_url}/start_job", json=incomplete_docs)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✓ SUCCESS! Full response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"Error: {response.json()}")

    except Exception as e:
        print(f"✗ Request failed: {e}")

    # Test 5: PDF Document Test
    print("\n=== TEST 5: PDF Document Test ===")
    try:
        # Check if PDF file exists
        import os
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
        if pdf_files:
            pdf_file = pdf_files[0]
            print(f"Found PDF: {pdf_file}")

            # For PDF testing, we'd need to implement file upload
            # For now, just test with text extraction from PDF name
            pdf_text = f"Testing with PDF document: {pdf_file}. This contains building construction compliance information."
            pdf_test_data = {
                "identifier_from_purchaser": "test_user_pdf",
                "input_data": {
                    "text": pdf_text
                }
            }

            response = requests.post(f"{base_url}/start_job", json=pdf_test_data)
            print(f"PDF Test Status Code: {response.status_code}")

            if response.status_code == 200:
                print("✓ PDF test successful!")
            else:
                print(f"✗ PDF test failed: {response.json()}")
        else:
            print("No PDF files found for testing")

    except Exception as e:
        print(f"✗ PDF test failed: {e}")

    print("\n=== COMPREHENSIVE TESTING COMPLETE ===")

if __name__ == "__main__":
    test_compliance_pipeline()