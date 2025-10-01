import requests
import json

# Test the API endpoints
def test_api():
    base_url = "http://0.0.0.0:8000"

    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return

    # Test input schema
    print("\nTesting input schema...")
    try:
        response = requests.get(f"{base_url}/input_schema")
        print(f"Schema: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Schema check failed: {e}")
        return

    # Test start job with Web3 compliance data
    print("\nTesting start_job endpoint...")
    test_data = {
        "identifier_from_purchaser": "web3_user_123",
        "region": "EU",
        "input_data": {
            "document_text": "Our DeFi protocol enables users to stake tokens and earn rewards. We have implemented KYC procedures and comply with GDPR requirements. The token is a utility token for governance purposes.",
            "document_type": "whitepaper"
        }
    }

    try:
        response = requests.post(f"{base_url}/start_job", json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Start job failed: {e}")

if __name__ == "__main__":
    test_api()