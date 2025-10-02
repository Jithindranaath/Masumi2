import os
import uvicorn
import uuid
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Dict
from masumi.config import Config
from masumi.payment import Payment, Amount
from crew_definition import ComplianceCrew
from logging_config import setup_logging

# Configure logging
logger = setup_logging()

# Load environment variables
load_dotenv(override=True)

# Retrieve API Keys and URLs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL")
PAYMENT_API_KEY = os.getenv("PAYMENT_API_KEY")
NETWORK = os.getenv("NETWORK")
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

logger.info("Starting application with configuration:")
logger.info(f"PAYMENT_SERVICE_URL: {PAYMENT_SERVICE_URL}")
logger.info(f"TEST_MODE: {TEST_MODE}")

# Initialize FastAPI
app = FastAPI(
    title="API following the Masumi API Standard",
    description="API for running Agentic Services tasks with Masumi payment integration",
    version="1.0.0"
)

# ─────────────────────────────────────────────────────────────────────────────
# Temporary in-memory job store (DO NOT USE IN PRODUCTION)
# ─────────────────────────────────────────────────────────────────────────────
jobs = {}
payment_instances = {}

# ─────────────────────────────────────────────────────────────────────────────
# Initialize Masumi Payment Config
# ─────────────────────────────────────────────────────────────────────────────
config = Config(
    payment_service_url=PAYMENT_SERVICE_URL,
    payment_api_key=PAYMENT_API_KEY
)

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────────────────────────────────────
class InputData(BaseModel):
    document_text: str = Field(..., min_length=10, description="Document content to analyze")
    document_type: str = Field(default="whitepaper", description="Type of document (whitepaper, tokenomics, legal, etc.)")
    priority: str = Field(default="normal", description="Analysis priority (low, normal, high)")

class StartJobRequest(BaseModel):
    identifier_from_purchaser: str = Field(..., min_length=3, description="Unique identifier for the purchaser")
    region: str = Field(default="EU", description="Compliance region (EU, US, UK, IN, etc.)")
    project_type: str = Field(default="general", description="Project type (DeFi, NFT, DAO, general)")
    urgency: str = Field(default="standard", description="Processing urgency (standard, expedited)")
    notification_email: str = Field(default="", description="Email for completion notifications")
    input_data: InputData

    class Config:
        json_schema_extra = {
            "example": {
                "identifier_from_purchaser": "web3_user_123",
                "region": "EU",
                "project_type": "DeFi",
                "urgency": "standard",
                "notification_email": "user@example.com",
                "input_data": {
                    "document_text": "Our DeFi protocol enables decentralized lending...",
                    "document_type": "whitepaper",
                    "priority": "high"
                }
            }
        }

class ProvideInputRequest(BaseModel):
    job_id: str

# ─────────────────────────────────────────────────────────────────────────────
# Email Notification Function
# ─────────────────────────────────────────────────────────────────────────────
def extract_compliance_score(result_text: str) -> str:
    """Extract compliance score from analysis result"""
    import re
    
    # Look for compliance score patterns
    score_patterns = [
        r'compliance[_\s]score["\s]*:?["\s]*([0-9.]+)',
        r'score["\s]*:?["\s]*([0-9.]+)',
        r'([0-9]+)%[\s]*compliant',
        r'([0-9.]+)[\s]*out[\s]*of[\s]*1'
    ]
    
    for pattern in score_patterns:
        match = re.search(pattern, result_text.lower())
        if match:
            score = float(match.group(1))
            if score <= 1:
                return f"{score*100:.1f}%"
            else:
                return f"{score:.1f}%"
    
    return "Analysis complete - see detailed results"

def send_completion_email(email: str, job_id: str, result: str):
    """Send email notification when analysis is complete"""
    if not email or email == "":
        return
    
    try:
        # Email configuration (you'd set these in .env)
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "noreply@compliance.ai")
        sender_password = os.getenv("SENDER_PASSWORD", "")
        
        if not sender_password:
            print(f"Email notification skipped - no SMTP credentials configured")
            return
            
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = f"Compliance Analysis Complete - Job {job_id[:8]}"
        
        body = f"""
        Your Web3 compliance analysis is complete!
        
        Job ID: {job_id}
        Status: Completed
        
        Analysis Summary:
        {result[:500]}...
        
        View full results at: http://your-api-url/status?job_id={job_id}
        
        Best regards,
        Compliance Analysis Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✉️  Email notification sent to {email}")
        
    except Exception as e:
        print(f"❌ Failed to send email notification: {str(e)}")

# ─────────────────────────────────────────────────────────────────────────────
# CrewAI Task Execution
# ─────────────────────────────────────────────────────────────────────────────
async def execute_crew_task(input_data: str, region: str = "EU", project_type: str = "general", urgency: str = "standard") -> tuple:
    """ Execute a CrewAI task with Web3 Compliance Analysis """
    import time
    start_time = time.time()
    
    logger.info(f"Starting Web3 compliance analysis for region: {region}, type: {project_type}, urgency: {urgency}")
    
    # Adjust processing based on urgency
    if urgency == "expedited":
        logger.info("EXPEDITED processing requested - prioritizing analysis")
    
    crew = ComplianceCrew(logger=logger)
    result = crew.crew.kickoff(inputs={"text": input_data, "region": region, "project_type": project_type})
    
    end_time = time.time()
    processing_time = f"{end_time - start_time:.2f} seconds"
    
    logger.info(f"Web3 compliance analysis completed successfully in {processing_time}")
    return result, processing_time

# ─────────────────────────────────────────────────────────────────────────────
# 1) Start Job (MIP-003: /start_job)
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/start_job")
async def start_job(data: StartJobRequest):
    """ Initiates a job and creates a payment request (or executes directly in test mode) """
    try:
        job_id = str(uuid.uuid4())
        agent_identifier = os.getenv("AGENT_IDENTIFIER")

        # Log the input text (truncate if too long)
        input_text = data.input_data.document_text
        truncated_input = input_text[:100] + "..." if len(input_text) > 100 else input_text
        logger.info(f"Received job request with input: '{truncated_input}'")
        logger.info(f"Starting job {job_id} with agent {agent_identifier}")

        # Check if we're in test mode
        if TEST_MODE:
            logger.info(f"TEST_MODE enabled - executing job {job_id} directly without payment verification")

            # Store job info (Test mode - no payment required)
            jobs[job_id] = {
                "status": "running",
                "payment_status": "test_mode",
                "payment_id": None,
                "input_data": data.input_data,
                "region": getattr(data, 'region', 'EU'),
                "project_type": getattr(data, 'project_type', 'general'),
                "urgency": getattr(data, 'urgency', 'standard'),
                "priority": getattr(data.input_data, 'priority', 'normal'),
                "document_type": getattr(data.input_data, 'document_type', 'whitepaper'),
                "notification_email": getattr(data, 'notification_email', ''),
                "result": None,
                "identifier_from_purchaser": data.identifier_from_purchaser,
                "test_mode": True,
                "created_at": time.time()
            }

            # Execute the task directly in test mode
            try:
                region = getattr(data, 'region', 'EU')
                project_type = getattr(data, 'project_type', 'general')
                urgency = getattr(data, 'urgency', 'standard')
                priority = getattr(data.input_data, 'priority', 'normal')
                document_type = getattr(data.input_data, 'document_type', 'whitepaper')
                
                # Log processing details
                logger.info(f"Processing {document_type} with {priority} priority")
                
                result, processing_time = await execute_crew_task(
                    data.input_data.document_text, region, project_type, urgency
                )
                
                # Extract compliance score
                compliance_score = extract_compliance_score(result.raw)
                
                logger.info(f"Web3 compliance analysis completed for job {job_id} in test mode")
                logger.info(f"Compliance Score: {compliance_score}")
                logger.info(f"Processing Time: {processing_time}")

                # Update job status
                jobs[job_id]["status"] = "completed"
                jobs[job_id]["payment_status"] = "completed"
                jobs[job_id]["result"] = result.raw
                jobs[job_id]["agent_results"] = {
                    "extraction": result.tasks_output[0].raw if len(result.tasks_output) > 0 else None,
                    "compliance_analysis": result.tasks_output[1].raw if len(result.tasks_output) > 1 else None,
                    "summary": result.tasks_output[2].raw if len(result.tasks_output) > 2 else None
                }

                # Return test mode response
                response = {
                    "status": "success",
                    "job_id": job_id,
                    "test_mode": True,
                    "message": "Job completed in test mode without payment verification",
                    "agentIdentifier": agent_identifier,
                    "identifierFromPurchaser": data.identifier_from_purchaser,
                    "region": region,
                    "project_type": project_type,
                    "urgency": urgency,
                    "document_type": document_type,
                    "priority": priority,
                    "result": result.raw,
                    "processing_time": processing_time,
                    "compliance_score": compliance_score,
                    "notification_email": getattr(data, 'notification_email', ''),
                    "analysis_metadata": {
                        "document_length": len(data.input_data.document_text),
                        "analysis_type": f"{region} {project_type} Compliance",
                        "priority_level": priority,
                        "urgency_level": urgency
                    }
                }
                
                # Print enhanced formatted output to console
                print("\n" + "="*70)
                print("🚀 WEB3 COMPLIANCE ANALYSIS COMPLETE")
                print("="*70)
                print(f"📊 Job ID: {job_id}")
                print(f"🌍 Region: {region}")
                print(f"🏗️  Project Type: {project_type}")
                print(f"📄 Document Type: {document_type}")
                print(f"⚡ Urgency: {urgency}")
                print(f"🎯 Priority: {priority}")
                print(f"✅ Status: {response['status']}")
                print(f"🧪 Test Mode: {response['test_mode']}")
                print(f"⏱️  Processing Time: {processing_time}")
                print(f"📊 Compliance Score: {compliance_score}")
                if getattr(data, 'notification_email', ''):
                    print(f"📧 Notification Email: {data.notification_email}")
                print("\n📋 DETAILED ANALYSIS RESULT:")
                print("-" * 50)
                print(result.raw)
                print("-" * 50)
                print(f"\n📈 ANALYSIS METADATA:")
                print(f"  • Document Length: {len(data.input_data.document_text)} characters")
                print(f"  • Analysis Type: {region} {project_type} Compliance")
                print(f"  • Priority Level: {priority}")
                print(f"  • Urgency Level: {urgency}")
                print("\n" + "="*70)
                
                # Send email notification if provided
                if hasattr(data, 'notification_email') and data.notification_email:
                    send_completion_email(data.notification_email, job_id, result.raw)
                
                return response
            except Exception as e:
                logger.error(f"Error executing task in test mode for job {job_id}: {str(e)}", exc_info=True)
                jobs[job_id]["status"] = "failed"
                jobs[job_id]["error"] = str(e)
                raise HTTPException(
                    status_code=500,
                    detail=f"Error executing task in test mode: {str(e)}"
                )
        else:
            # Normal payment flow
            logger.info(f"Normal mode - creating payment request for job {job_id}")

            # Define payment amounts
            payment_amount = os.getenv("PAYMENT_AMOUNT", "10000000")  # Default 10 ADA
            payment_unit = os.getenv("PAYMENT_UNIT", "lovelace") # Default lovelace

            amounts = [Amount(amount=payment_amount, unit=payment_unit)]
            logger.info(f"Using payment amount: {payment_amount} {payment_unit}")

            # Create a payment request using Masumi
            payment = Payment(
                agent_identifier=agent_identifier,
                #amounts=amounts,
                config=config,
                identifier_from_purchaser=data.identifier_from_purchaser,
                input_data=data.input_data.dict(),
                network=NETWORK
            )

            logger.info("Creating payment request...")
            payment_request = await payment.create_payment_request()
            payment_id = payment_request["data"]["blockchainIdentifier"]
            payment.payment_ids.add(payment_id)
            logger.info(f"Created payment request with ID: {payment_id}")

            # Store job info (Awaiting payment)
            jobs[job_id] = {
                "status": "awaiting_payment",
                "payment_status": "pending",
                "payment_id": payment_id,
                "input_data": data.input_data,
                "region": getattr(data, 'region', 'EU'),
                "project_type": getattr(data, 'project_type', 'general'),
                "result": None,
                "identifier_from_purchaser": data.identifier_from_purchaser,
                "test_mode": False
            }

            async def payment_callback(payment_id: str):
                await handle_payment_status(job_id, payment_id)

            # Start monitoring the payment status
            payment_instances[job_id] = payment
            logger.info(f"Starting payment status monitoring for job {job_id}")
            await payment.start_status_monitoring(payment_callback)

            # Return the response in the required format
            return {
                "status": "success",
                "job_id": job_id,
                "blockchainIdentifier": payment_request["data"]["blockchainIdentifier"],
                "submitResultTime": payment_request["data"]["submitResultTime"],
                "unlockTime": payment_request["data"]["unlockTime"],
                "externalDisputeUnlockTime": payment_request["data"]["externalDisputeUnlockTime"],
                "agentIdentifier": agent_identifier,
                "sellerVkey": os.getenv("SELLER_VKEY"),
                "identifierFromPurchaser": data.identifier_from_purchaser,
                "amounts": amounts,
                "input_hash": payment.input_hash,
                "payByTime": payment_request["data"]["payByTime"],
                "test_mode": False
            }
    except KeyError as e:
        logger.error(f"Missing required field in request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Bad Request: If input_data or identifier_from_purchaser is missing, invalid, or does not adhere to the schema."
        )
    except Exception as e:
        logger.error(f"Error in start_job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Error processing request: {str(e)}"
        )

# ─────────────────────────────────────────────────────────────────────────────
# 2) Process Payment and Execute AI Task
# ─────────────────────────────────────────────────────────────────────────────
async def handle_payment_status(job_id: str, payment_id: str) -> None:
    """ Executes CrewAI task after payment confirmation (or handles test mode) """
    try:
        # Check if this job is in test mode
        if jobs[job_id].get("test_mode", False):
            logger.info(f"Job {job_id} is in test mode - no payment processing needed")
            return

        logger.info(f"Payment {payment_id} completed for job {job_id}, executing task...")

        # Update job status to running
        jobs[job_id]["status"] = "running"
        logger.info(f"Input data: {jobs[job_id]["input_data"]}")

        # Execute the Web3 compliance analysis task
        input_text = jobs[job_id]["input_data"].document_text
        region = jobs[job_id].get("region", "EU").upper()
        project_type = jobs[job_id].get("project_type", "general")
        result = await execute_crew_task(input_text, region, project_type)
        result_dict = result.json_dict
        logger.info(f"Web3 compliance analysis completed for job {job_id}")

        # Mark payment as completed on Masumi
        # Use a shorter string for the result hash
        await payment_instances[job_id].complete_payment(payment_id, result_dict)
        logger.info(f"Payment completed for job {job_id}")

        # Update job status
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["payment_status"] = "completed"
        jobs[job_id]["result"] = result.raw

        # Stop monitoring payment status
        if job_id in payment_instances:
            payment_instances[job_id].stop_status_monitoring()
            del payment_instances[job_id]
    except Exception as e:
        logger.error(f"Error processing payment {payment_id} for job {job_id}: {str(e)}", exc_info=True)
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

        # Still stop monitoring to prevent repeated failures
        if job_id in payment_instances:
            payment_instances[job_id].stop_status_monitoring()
            del payment_instances[job_id]

# ─────────────────────────────────────────────────────────────────────────────
# 3) Check Job and Payment Status (MIP-003: /status)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/status")
async def get_status(job_id: str):
    """ Retrieves the current status of a specific job """
    logger.info(f"Checking status for job {job_id}")
    if job_id not in jobs:
        logger.warning(f"Job {job_id} not found")
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    # Check if this is a test mode job
    if job.get("test_mode", False):
        logger.info(f"Job {job_id} is in test mode - returning test mode status")
        result = job.get("result")

        return {
            "job_id": job_id,
            "status": job["status"],
            "payment_status": job["payment_status"],
            "test_mode": True,
            "result": result
        }

    # Check latest payment status if payment instance exists (normal mode)
    if job_id in payment_instances:
        try:
            status = await payment_instances[job_id].check_payment_status()
            job["payment_status"] = status.get("data", {}).get("status")
            logger.info(f"Updated payment status for job {job_id}: {job['payment_status']}")
        except ValueError as e:
            logger.warning(f"Error checking payment status: {str(e)}")
            job["payment_status"] = "unknown"
        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}", exc_info=True)
            job["payment_status"] = "error"

    result = job.get("result")
    agent_results = job.get("agent_results", {})

    return {
        "job_id": job_id,
        "status": job["status"],
        "payment_status": job["payment_status"],
        "test_mode": False,
        "result": result,
        "agent_results": agent_results
    }

# ─────────────────────────────────────────────────────────────────────────────
# 4) Check Server Availability (MIP-003: /availability)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/availability")
async def check_availability():
    """ Checks if the server is operational """

    return {"status": "available", "type": "masumi-agent", "message": "Server operational."}
    # Commented out for simplicity sake but its recommended to include the agentIdentifier
    #return {"status": "available","agentIdentifier": os.getenv("AGENT_IDENTIFIER"), "message": "The server is running smoothly."}

# ─────────────────────────────────────────────────────────────────────────────
# 5) Retrieve Input Schema (MIP-003: /input_schema)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/input_schema")
async def input_schema():
    """
    Returns the expected input schema for the /start_job endpoint.
    Fulfills MIP-003 /input_schema endpoint.
    """
    return StartJobRequest.model_json_schema()

# ─────────────────────────────────────────────────────────────────────────────
# 6) Health Check
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    """
    Returns the health of the server.
    """
    return {
        "status": "healthy"
    }

# ─────────────────────────────────────────────────────────────────────────────
# Main Logic if Called as a Script
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("Running CrewAI as standalone script is not supported when using payments.")
    print("Start the API using `python main.py api` instead.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        print("Starting FastAPI server with Masumi integration...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        main()
