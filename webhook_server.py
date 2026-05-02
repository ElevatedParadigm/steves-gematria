"""
Webhook Server for Steve's Gematria Image Analysis System
Receives image URLs or file uploads via POST requests and triggers gematria analysis workflow.
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, HttpUrl, field_validator

# ============== MODEL DEFINITIONS ==============

class ImageAnalysisRequest(BaseModel):
    """Model for receiving image analysis requests"""
    url: HttpUrl
    analysis_type: str = "gematria"  # gematria, full_analysis, pattern_match
    
    @field_validator('url')
    def validate_url(cls, v):
        try:
            return str(v)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid URL format: {e}")

class FileUploadRequest(BaseModel):
    """Model for receiving file uploads"""
    filename: str
    content_type: str = None

class MetadataRequest(BaseModel):
    """Model for receiving metadata/context info"""
    anchor_terms: list[str] = []
    priority_domains: list[str] = []
    context_description: str = ""

# ============== CONFIGURATION ==============
BASE_DIR = Path.home() / ".hermes" / "gematria"
ANALYSIS_LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"
TEMP_DIR = BASE_DIR / "temp"

# Ensure directories exist
for dir_path in [ANALYSIS_LOGS_DIR, REPORTS_DIR, TEMP_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(BASE_DIR / "logs" / "webhook_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("webhook-server")

# ============== ANALYSIS WORKFLOW INTERFACE ==============

class AnalysisWorkflow:
    """Interface for the gematria analysis workflow system"""
    
    @staticmethod
    async def analyze_image_url(url: str, analysis_type: str = "gematria") -> dict:
        """Route to existing gematria analysis workflow (placeholder)"""
        logger.info(f"Analyzing image URL: {url} - Type: {analysis_type}")
        
        return {
            "status": "processing",
            "message": f"Image analysis request received for: {url}",
            "workflow_id": hashlib.md5(f"{url}{datetime.now()}".encode()).hexdigest()[:8]
        }
    
    @staticmethod
    async def analyze_file(filepath: str, anchor_terms: list = None) -> dict:
        """Route to existing gematria analysis workflow for local files"""
        logger.info(f"Analyzing file: {filepath}")
        
        return {
            "status": "processing", 
            "message": f"File analysis request received: {os.path.basename(filepath)}",
            "workflow_id": hashlib.md5(f"{filepath}{datetime.now()}".encode()).hexdigest()[:8]
        }
    
    @staticmethod
    async def trigger_analysis_workflow(data: dict) -> dict:
        """Trigger existing gematria-analysis-workflow"""
        logger.info(f"Triggering workflow with data keys: {list(data.keys())}")
        
        try:
            from hermes_tools import delegate_task
            
            task = {
                "goal": f"Perform gematria analysis on the provided image/data",
                "context": json.dumps({
                    "input_type": data.get("type", "url"),
                    "analysis_request": data.get("request", {}),
                    "priority": data.get("priority_domains")
                }),
                "toolsets": ["browser", "file"]
            }
            
            result = delegate_task(tasks=[task])
            return {"status": "queued", "message": "Analysis queued successfully"}
            
        except ImportError:
            logger.info("Not using delegated workflow - returning placeholder response")
            return {
                "status": "simulated",
                "workflow_id": hashlib.md5(f"{data.get('url', 'file')}{datetime.now()}".encode()).hexdigest()[:8]
            }

analysis_workflow = AnalysisWorkflow()
import hashlib

# ============== API ENDPOINTS ==============

app = FastAPI(
    title="Steve's Gematria Webhook Server",
    description="Image analysis webhook handler for gematria pattern recognition",
    version="1.0.0"
)

@app.post("/webhook/image")
async def handle_image_webhook(request: ImageAnalysisRequest):
    """Handle image URL webhook requests"""
    logger.info(f"Received image webhook: {request.url}")
    
    try:
        result = await analysis_workflow.analyze_image_url(
            str(request.url),
            request.analysis_type
        )
        
        return JSONResponse(status_code=202, content=result)
        
    except Exception as e:
        logger.error(f"Error processing image webhook: {e}")
        return JSONResponse(
            status_code=500, 
            content={"status": "error", "message": str(e)}
        )

@app.post("/webhook/file")
async def handle_file_webhook(request: FileUploadRequest):
    """Handle file upload webhook requests"""
    logger.info(f"Received file upload webhook")
    
    try:
        if "file" not in request.headers or "image_url" not in request.headers:
            return JSONResponse(
                status_code=400, 
                content={"status": "error", "message": "Missing file or image_url"}
            )
            
        temp_file = TEMP_DIR / f"{request.filename}.tmp"
        
        if request.file:
            with open(temp_file, "wb") as f:
                f.write(request.file.read())
            
            logger.info(f"Saved uploaded file to: {temp_file}")
            
            result = await analysis_workflow.analyze_file(str(temp_file))
            return JSONResponse(status_code=202, content=result)
            
    except Exception as e:
        logger.error(f"Error processing file webhook: {e}")
        return JSONResponse(
            status_code=500, 
            content={"status": "error", "message": str(e)}
        )

@app.post("/webhook/raw")
async def handle_raw_webhook(request: Request):
    """Handle raw POST requests (flexible webhook endpoint)"""
    logger.info("Received raw webhook request")
    
    try:
        content_type = request.headers.get("content-type", "")
        body = await request.json() if "application/json" in content_type else {}
        
        image_url = body.get("image_url") or body.get("url")
        
        if image_url:
            result = await analysis_workflow.analyze_image_url(image_url)
            return JSONResponse(status_code=202, content=result)
            
    except Exception as e:
        logger.error(f"Error processing raw webhook: {e}")
        if isinstance(e, ValueError) and "JSON" in str(type(e).__name__):
            return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid JSON payload"})
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Steve's Gematria Webhook Server",
        "timestamp": datetime.now().isoformat(),
        "base_path": str(BASE_DIR)
    }

@app.get("/logs")
async def get_logs(limit: int = 50):
    """Get recent logs (for debugging)"""
    log_file = ANALYSIS_LOGS_DIR / "webhook_server.log"
    if log_file.exists():
        with open(log_file, 'r') as f:
            lines = f.readlines()[-limit:]
        return {"logs": lines}
    return {"message": "No logs found"}

@app.get("/stats")
async def get_stats():
    """Basic statistics about webhook activity"""
    stats = {
        "total_requests": len(list(ANALYSIS_LOGS_DIR.glob("webhook_*"))),
        "recent_files": len(list(REPORTS_DIR.glob("*")), 0) if ANALYSIS_LOGS_DIR.exists() else 0
    }
    return stats

# ============== RUN SERVER ==============

if __name__ == "__main__":
    import uvicorn
    
    print("🗝️  Starting Steve's Gematria Webhook Server...")
    print(f"📍 Base directory: {BASE_DIR}")
    print(f"📖 Logs at: {ANALYSIS_LOGS_DIR / 'webhook_server.log'}")
    print()
    
    uvicorn.run(
        "webhook_server:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
        workers=1
    )
