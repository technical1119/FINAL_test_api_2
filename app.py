from crypto_rank import get_links_from_webpage, get_social_links_from_overview, get_website_content_selenium, get_website_content_http
from defilama import get_defilama_project_details, get_defilama_projects

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Optional

import uvicorn

# Load environment variables
load_dotenv()

# Define request models
class URLRequest(BaseModel):
    url: str

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get_links")
async def get_links(request: URLRequest):
    try:
        links = get_links_from_webpage(request.url)
        if links is None:
            raise HTTPException(status_code=500, detail="Failed to get links")
        return {"content": links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_social")
async def get_social(request: URLRequest):
    try:
        social_links = get_social_links_from_overview(request.url)
        if social_links is None:
            raise HTTPException(status_code=500, detail="Failed to get social links")
        return {"social_links": social_links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_content_http")
async def get_content_http(request: URLRequest):
    try:
        content = get_website_content_http(request.url)
        if content is None:
            raise HTTPException(status_code=500, detail="Failed to get content")
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/get_content_selenium")
async def get_content_selenium(request: URLRequest):
    try:
        content = get_website_content_selenium(request.url)
        if content is None:
            raise HTTPException(status_code=500, detail="Failed to get content")
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#------------------------------------------Defilama-----------------------------------------------------

@app.get("/get_defilama_projects")
async def get_defilama_projects_endpoint():
    try:
        # Call the scraping function with a different name
        projects = await get_defilama_projects()  # Note: not async if using Selenium
        if projects is None:
            raise HTTPException(status_code=500, detail="Failed to fetch projects")
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/get_defilama_project_details")
def get_project_details_endpoint(request: URLRequest):
    try:
        # Validate URL
        if not request.url or not request.url.startswith("https://defillama.com/protocol/"):
            raise HTTPException(status_code=400, detail="Invalid DeFiLlama URL")

        # Get project details
        social_links = get_defilama_project_details(request.url)
        
        if social_links is None:
            raise HTTPException(status_code=500, detail="Failed to fetch project details")
            
        return {"social_links": social_links}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 6000))
    uvicorn.run(app, host="0.0.0.0", port=port)
