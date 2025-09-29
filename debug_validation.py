from pydantic import BaseModel, ValidationError
import json

class StartJobRequest(BaseModel):
    identifier_from_purchaser: str
    input_data: dict[str, str]

    class Config:
        json_schema_extra = {
            "example": {
                "identifier_from_purchaser": "example_purchaser_123",
                "input_data": {
                    "text": "Write a story about a robot learning to paint"
                }
            }
        }

# Test the model validation
def test_validation():
    test_data = {
        "identifier_from_purchaser": "test_user_123",
        "input_data": {
            "text": "Building permit approved by Municipal Corporation"
        }
    }

    print("Testing Pydantic model validation...")
    print(f"Test data: {json.dumps(test_data, indent=2)}")

    try:
        model = StartJobRequest(**test_data)
        print("✓ Validation successful!")
        print(f"identifier_from_purchaser: {model.identifier_from_purchaser}")
        print(f"input_data: {model.input_data}")
        print(f"input_data['text']: {model.input_data['text']}")
        return True
    except ValidationError as e:
        print(f"✗ Validation failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_validation()