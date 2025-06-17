from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="LangGraph Flow API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "langgraph-flow-backend"}

@app.get("/")
async def root():
    return {"message": "LangGraph Flow API", "version": "1.0.0"}

# Add your API endpoints here
