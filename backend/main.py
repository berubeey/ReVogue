from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from dotenv import load_dotenv
from agents.fashion_designer_agent import FashionDesignerAgent
from agents.base_agent import AgentState, SharedUserInput
import asyncio

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the fashion designer agent
fashion_designer = FashionDesignerAgent()

class UserProfile(BaseModel):
    gender: str
    height_cm: int
    skin_tone: str
    occupation: str
    style_preference: List[str]
    daily_schedule: Optional[List[dict]] = None
    wardrobe_items: Optional[List[dict]] = None

@app.post("/analyze-fashion")
async def analyze_fashion(profile: UserProfile):
    """Analyze fashion based on user profile and generate recommendations"""
    try:
        # Create agent state
        state = AgentState(
            user_input=SharedUserInput(
                user_input="分析穿搭",
                profession=profile.occupation,
                personality="外向",  # Default value
                gender=profile.gender,
                height_cm=profile.height_cm,
                skin_tone=profile.skin_tone,
                style_preference=profile.style_preference,
                schedule_summary="",  # Will be filled by personal secretary
                weather_summary="",   # Will be filled by personal secretary
                feedback_history=[],
                wardrobe_items=profile.wardrobe_items or []
            ),
            context={}
        )
        
        # Process with fashion designer agent
        result = await fashion_designer.process(state)
        
        return {
            "status": "success",
            "recommendations": result.context.get("recommendations", ""),
            "conversation_history": result.conversation_history,
            "error": result.error
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload and analyze an image"""
    try:
        # Save the uploaded file
        file_location = f"images/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        
        return {
            "status": "success",
            "message": "Image uploaded successfully",
            "file_path": file_location
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 