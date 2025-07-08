from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # lets us make requests from frontend to backend
from pydantic import BaseModel
from dotenv import load_dotenv
from api_parser import get_api_parser
from ontology_mapper import map_api_to_ontology
import os
from typing import Optional

# load environment variables
load_dotenv()

# create FastAPI app
app = FastAPI(
    title="Open Integrate API",
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

class ParseDocRequest(BaseModel):
    url: str

class MapOntologyRequest(BaseModel):
    api_spec: dict
    acho_token: Optional[str] = None

class IngestDataRequest(BaseModel):
    api_spec: dict
    mapping: dict
    acho_token: Optional[str] = None

# basic health check endpoint
@app.get("/")
async def root():
    return {"message": "Open Integrate API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/parse-doc")
async def parse_doc(request: ParseDocRequest):
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Use the API parser to analyze the documentation
    api_parser = get_api_parser()
    result = api_parser.parse_api_documentation(request.url.strip())
    
    if result['status'] == 'error':
        raise HTTPException(status_code=500, detail=f"Failed to parse API documentation: {result.get('error', 'Unknown error')}")
    
    return result

@app.post("/api/map-ontology")
async def map_ontology(request: MapOntologyRequest):
    # Use provided token or fall back to environment variable
    acho_token = request.acho_token or os.getenv('ACHO_TOKEN')
    if not acho_token:
        raise HTTPException(status_code=400, detail="ACHO_TOKEN not provided and not found in environment")
    mapping = map_api_to_ontology(request.api_spec, acho_token)
    return mapping

@app.post("/api/ingest-data")
async def ingest_data(request: IngestDataRequest):
    from data_ingestion_agent import execute_ingestion_sdk
    # Use provided token or fall back to environment variable
    acho_token = request.acho_token or os.getenv('ACHO_TOKEN')
    if not acho_token:
        raise HTTPException(status_code=400, detail="ACHO_TOKEN not provided and not found in environment")
    result = execute_ingestion_sdk(request.api_spec, request.mapping, acho_token)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
