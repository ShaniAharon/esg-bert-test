import random
import time
from esg_scoring import analyze_pdf_url
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import uvicorn
import httpx
import asyncio

app = FastAPI()

# Set up CORS middleware options
origins = [
    "*",
    "https://begzesyud7.us-east-2.awsapprunner.com/"
    "https://jrhkpcmcz5.us-east-2.awsapprunner.com/",
    "http://localhost:80",
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins that are allowed to make requests
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

    
# Analyze PDF endpoint
class PDFRequest(BaseModel):
    url: str

@app.post("/analyze-pdf")
async def analyze_pdf(pdf_request: PDFRequest):
    try:
        esg_result = analyze_pdf_url(pdf_request.url)
        return esg_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))    

#Health Check Endpoint
@app.get("/health")
def read_health():
    print('server awake')
    return {"status": "healthy"}

async def keep_awake():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                await client.get("https://search-res-microservice.onrender.com/health")
            await asyncio.sleep(600)  # Sleep for 10 minutes
        except Exception as e:
            print(f"Error keeping the service awake: {e}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(keep_awake())



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))