import os
from dotenv import load_dotenv
from google import genai

# Read the API key from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

if not api_key or api_key == "your_gemini_api_key_here":
    print("API key not found. Check your .env file.")
else:
    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=model,
            contents="Reply with: Gemini API is working!"
        )

        print("SUCCESS! Gemini API is working.")
        print("Gemini response:", response.text)

        client.close()

    except Exception as error:
        print("Gemini API test failed.")
        print("Error:", error)