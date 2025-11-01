import google.generativeai as genai
import os

# --- 1. LOAD API KEY ---
YOUR_API_KEY = os.environ.get("GOOGLE_API_KEY")

if YOUR_API_KEY is None:
    print("❌ Error: 'GOOGLE_API_KEY' environment variable not set.")
    print("   Please CLOSE and REOPEN your terminal.")
    exit()

print("Connecting to Google AI with your API key...")

try:
    genai.configure(api_key=YOUR_API_KEY)

    # --- 2. LIST ALL AVAILABLE MODELS ---
    print("\n--- Available Models ---")

    # This loop asks the API to list all models it supports
    # for the `generateContent` method.
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ {m.name}")

    print("\n--------------------------")
    print("Please copy the list above and paste it back.")

except Exception as e:
    print(f"\n❌ An error occurred: {e}")