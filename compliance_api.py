from fastapi import FastAPI
from pydantic import BaseModel
import uuid
from conditional_workflow import ConditionalComplianceWorkflow

app = FastAPI()

# In-memory job storage
jobs = {}

class JobRequest(BaseModel):
    project_type: str
    jurisdiction: str
    document: str

def check_payment() -> bool:
    # Simulate payment check - always returns True for now
    return True

@app.post("/start_job")
async def start_job(request: JobRequest):
    job_id = str(uuid.uuid4())
    
    # Store initial job
    jobs[job_id] = {
        "status": "payment_pending",
        "project_type": request.project_type,
        "jurisdiction": request.jurisdiction,
        "document": request.document,
        "result": None
    }
    
    # Check payment first
    if not check_payment():
        jobs[job_id]["status"] = "payment_failed"
        return {"job_id": job_id, "status": "payment_failed", "error": "Payment verification failed"}
    
    # Payment succeeded, update status and run workflow
    jobs[job_id]["status"] = "processing"
    
    # Initialize conditional workflow
    workflow = ConditionalComplianceWorkflow()
    
    # Run conditional workflow
    result = workflow.run_workflow(request.document, request.jurisdiction)
    
    # Update job with result
    jobs[job_id]["status"] = result["status"]
    jobs[job_id]["result"] = result
    
    return {"job_id": job_id, "status": result["status"], "result": result}

@app.get("/status")
async def get_status(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    
    return {
        "job_id": job_id,
        "status": jobs[job_id]["status"],
        "result": jobs[job_id]["result"]
    }