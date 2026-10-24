import os
from supabase import create_client, Client
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="FDE Cold Call Assistant")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://aditya-fde-assignment.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
STAGES = [
    {"id": 1, "stage_name": "Opening", "purpose": "Start the conversation politely",
     "prospect_says": "Hello, who is this?", "suggested_action": "Introduce yourself and ask permission to continue"},
    {"id": 2, "stage_name": "Reason for Calling", "purpose": "Explain why you called",
     "prospect_says": "What is this regarding?", "suggested_action": "Give a brief, relevant reason"},
    {"id": 3, "stage_name": "Build Rapport", "purpose": "Create a connection",
     "prospect_says": "I am busy right now", "suggested_action": "Acknowledge their time and stay respectful"},
    {"id": 4, "stage_name": "Discover Needs", "purpose": "Understand their challenges",
     "prospect_says": "We already have a solution", "suggested_action": "Ask about their current process"},
    {"id": 5, "stage_name": "Present Value", "purpose": "Explain relevant benefits",
     "prospect_says": "How will this help us?", "suggested_action": "Connect benefits to their needs"},
    {"id": 6, "stage_name": "Handle Objections", "purpose": "Address concerns",
     "prospect_says": "It sounds expensive", "suggested_action": "Ask a clarifying question and respond honestly"},
    {"id": 7, "stage_name": "Agree Next Step", "purpose": "Secure a practical next step",
     "prospect_says": "Send me some details", "suggested_action": "Agree on a follow-up or meeting"},
    {"id": 8, "stage_name": "Close Call", "purpose": "End clearly and politely",
     "prospect_says": "Thank you for calling", "suggested_action": "Confirm the outcome and thank the prospect"},
]

class StartCall(BaseModel):
    prospect_name: str

class StageResult(BaseModel):
    stage_id: int
    what_happened: str
    prospect_words: str = ""

class CloseCall(BaseModel):
    outcome: str

calls = {}

@app.get("/")
def home():
    return {"message": "FDE Cold Call Assistant API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/stages")
def get_stages():
    return STAGES

@app.post("/calls")
def start_call(data: StartCall):
    import uuid
    call_id = str(uuid.uuid4())
    calls[call_id] = {
        "id": call_id,
        "prospect_name": data.prospect_name,
        "current_stage": 1,
        "outcome": None,
        "stage_results": []
    }
    return calls[call_id]

@app.post("/calls/{call_id}/stage")
def save_stage(call_id: str, data: StageResult):
    if call_id not in calls:
        raise HTTPException(status_code=404, detail="Call not found")
    if not 1 <= data.stage_id <= 8:
        raise HTTPException(status_code=400, detail="Invalid stage")
    calls[call_id]["stage_results"].append(data.model_dump())
    calls[call_id]["current_stage"] = min(data.stage_id + 1, 8)
    return calls[call_id]

@app.post("/calls/{call_id}/close")
def close_call(call_id: str, data: CloseCall):
    if call_id not in calls:
        raise HTTPException(status_code=404, detail="Call not found")
    calls[call_id]["outcome"] = data.outcome
    return calls[call_id]

@app.get("/calls")
def list_calls():
    return list(calls.values())