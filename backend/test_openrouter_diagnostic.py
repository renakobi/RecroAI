"""
Diagnostic script for OpenRouter API configuration
Run this to check your OpenRouter setup and identify issues.
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("OpenRouter Configuration Diagnostic")
print("=" * 60)

# Check environment variables
print("\n1. Environment Variables:")
provider = os.getenv("LLM_PROVIDER", "openai").lower()
print(f"   LLM_PROVIDER: {provider}")

api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
if api_key:
    masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
    print(f"   API Key: {masked_key} (found)")
else:
    print(f"   API Key: NOT SET [ERROR]")

base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
print(f"   Base URL: {base_url}")

model = os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL")
if model:
    print(f"   Model: {model}")
    # Check model format
    if provider == "openrouter":
        if "/" not in model:
            print(f"   [WARNING] OpenRouter models need provider prefix!")
            print(f"      Current: {model}")
            print(f"      Should be: openai/{model} or anthropic/claude-3-haiku")
    else:
        print(f"   Model format looks OK")
else:
    print(f"   Model: NOT SET [ERROR]")

# Test import
print("\n2. Testing imports:")
try:
    from app.services.openai_client import get_client, get_model
    print("   [OK] Imports successful")
except Exception as e:
    print(f"   [ERROR] Import error: {e}")
    exit(1)

# Test client creation
print("\n3. Testing client creation:")
try:
    if provider == "openrouter":
        if not api_key:
            print("   [ERROR] Cannot test: API key not set")
        else:
            client = get_client()
            print("   [OK] Client created successfully")
            print(f"   Client base_url: {client.base_url}")
    else:
        print("   [SKIP] Skipping (not using OpenRouter)")
except ValueError as e:
    print(f"   [ERROR] Client creation failed: {e}")
except Exception as e:
    print(f"   [ERROR] Unexpected error: {e}")

# Test model retrieval
print("\n4. Testing model retrieval:")
try:
    retrieved_model = get_model()
    print(f"   [OK] Model retrieved: {retrieved_model}")
except ValueError as e:
    print(f"   [ERROR] Model retrieval failed: {e}")
except Exception as e:
    print(f"   [ERROR] Unexpected error: {e}")

# Test API call (if everything else works)
if provider == "openrouter" and api_key and model:
    print("\n5. Testing API call:")
    try:
        client = get_client()
        model_name = get_model()
        
        print(f"   Calling OpenRouter with model: {model_name}")
        response = client.chat.completions.create(
            model=model_name,
            temperature=0,
            messages=[
                {"role": "user", "content": "Say 'OK' in JSON format: {\"status\": \"ok\"}"}
            ],
            max_tokens=50
        )
        
        content = response.choices[0].message.content
        print(f"   [OK] API call successful!")
        print(f"   Response: {content[:100]}...")
        
    except Exception as e:
        print(f"   [ERROR] API call failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Common error messages
        error_str = str(e).lower()
        if "model" in error_str and ("not found" in error_str or "invalid" in error_str):
            print("\n   💡 TIP: Model name might be wrong. OpenRouter requires:")
            print("      - Provider prefix: openai/gpt-4o-mini")
            print("      - Not just: gpt-4o-mini")
        elif "401" in error_str or "unauthorized" in error_str:
            print("\n   💡 TIP: Check your API key is correct")
        elif "404" in error_str:
            print("\n   💡 TIP: Check base URL is correct: https://openrouter.ai/api/v1")

print("\n" + "=" * 60)
print("Diagnostic complete!")
print("=" * 60)

