from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # lets us make requests from frontend to backend
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

# create FastAPI app
app = FastAPI(
    title="Open Integrate",
    description="AI-powered data integration platform",
    version="1.0.0"
)

# configure cors (cross origin resource sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # frontend(3000) talks to backend(8000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# basic health check endpoint
@app.get("/")
async def root():
    return {"message": "Open Integrate API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
