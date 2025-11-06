import replicate
import os

# Test if replicate is working
os.environ["REPLICATE_API_TOKEN"] = "test_token"

try:
    # Try to get model info
    model = replicate.models.get("black-forest-labs/flux-schnell")
    print(f"Model found: {model.name}")
    print(f"Latest version: {model.latest_version.id if model.latest_version else 'None'}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e).__name__}")
