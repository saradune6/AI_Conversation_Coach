from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os
import glob
import google.generativeai as genai  # Import Google's Gemini SDK
from dotenv import load_dotenv  # ✅ Load .env file

# ✅ Load Environment Variables from .env
load_dotenv()

# ✅ Get API Key from Environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("❌ ERROR: Google API Key is missing! Add it to the .env file.")

# ✅ Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (Frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Initialize Gemini Model
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    raise RuntimeError(f"❌ ERROR: Failed to initialize Gemini Model → {str(e)}")

# ✅ Define Input Schema
class UserInput(BaseModel):
    text: str  # Accepts any general input

# ✅ Route to process user input and get a generic response
@app.post("/process_request")
async def process_request(user_input: UserInput):
    print(f"User input received: {user_input.text}")  # Debugging

    # ✅ No hardcoded prompt structure – it will work for any input
    prompt = f"{user_input.text}"

    try:
        # Ensure model is initialized
        if not model:
            raise RuntimeError("Gemini model is not initialized!")

        # Generate response from Gemini
        response = model.generate_content(prompt)

        # Validate response format
        if not response or not hasattr(response, "text"):
            raise ValueError("Gemini API returned an unexpected response format.")

        return {"message": "Response generated successfully", "response": response.text}

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")  # Log error for debugging
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ✅ Function to get the latest Python file
def get_latest_python_file():
    python_files = glob.glob("*.py")  # Get all .py files in the directory
    if not python_files:
        return None
    latest_file = max(python_files, key=os.path.getctime)  # Get most recently created file
    return latest_file

# ✅ Route to get the latest Python file content
@app.get("/latest_code")
async def latest_code():
    latest_file = get_latest_python_file()
    if not latest_file:
        return JSONResponse(content={"error": "No Python files found"}, status_code=404)

    with open(latest_file, "r") as f:
        code_content = f.read()

    return {"filename": latest_file, "content": code_content}

# ✅ Route to serve UI (index.html)
@app.get("/")
async def serve_ui():
    return FileResponse("static/index.html")

# ✅ Run FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
