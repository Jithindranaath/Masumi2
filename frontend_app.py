from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import tempfile
from conditional_workflow import BuildingComplianceWorkflow

app = FastAPI()

# Store workflow results
workflow_results = {}

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Compliance Agent Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            .upload-section { border: 2px dashed #ddd; padding: 30px; text-align: center; margin-bottom: 20px; border-radius: 8px; }
            .upload-section:hover { border-color: #007bff; }
            input[type="file"] { margin: 10px 0; }
            select, input[type="text"] { width: 200px; padding: 8px; margin: 10px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            button:disabled { background: #ccc; cursor: not-allowed; }
            .process-section { margin-top: 30px; }
            .agent-step { margin: 15px 0; padding: 15px; border-left: 4px solid #ddd; background: #f8f9fa; border-radius: 4px; }
            .agent-step.active { border-left-color: #007bff; background: #e3f2fd; }
            .agent-step.completed { border-left-color: #28a745; background: #d4edda; }
            .agent-step.failed { border-left-color: #dc3545; background: #f8d7da; }
            .step-title { font-weight: bold; margin-bottom: 8px; }
            .step-result { background: white; padding: 15px; border-radius: 4px; margin-top: 8px; font-family: Arial, sans-serif; font-size: 14px; max-height: 200px; overflow-y: auto; border: 1px solid #ddd; }
            .loading { display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #007bff; border-radius: 50%; animation: spin 1s linear infinite; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Compliance Agent Dashboard</h1>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-section">
                    <h3>📄 Upload Compliance Document</h3>
                    <input type="file" name="file" accept=".pdf,.txt,.doc,.docx" required>
                    <br>
                    <select name="jurisdiction" required>
                        <option value="">Select Jurisdiction</option>
                        <option value="India">India</option>
                        <option value="EU">European Union</option>
                        <option value="US">United States</option>
                    </select>
                    <br>
                    <button type="submit" id="submitBtn">🚀 Start Compliance Check</button>
                </div>
            </form>

            <div class="process-section" id="processSection" style="display: none;">
                <h3>🤖 Agent Processing Status</h3>
                
                <div class="agent-step" id="step1">
                    <div class="step-title">Step 1: Document Extraction Agent</div>
                    <div>Parsing and extracting text from uploaded document...</div>
                    <div class="step-result" id="result1"></div>
                </div>

                <div class="agent-step" id="step2">
                    <div class="step-title">Step 2: Compliance Matching Agent</div>
                    <div>Checking document against compliance rules...</div>
                    <div class="step-result" id="result2"></div>
                </div>

                <div class="agent-step" id="step3">
                    <div class="step-title">Step 3: Summary Generation Agent</div>
                    <div>Generating compliance summary and checklist...</div>
                    <div class="step-result" id="result3"></div>
                </div>
            </div>
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const submitBtn = document.getElementById('submitBtn');
                const processSection = document.getElementById('processSection');
                
                // Show process section and disable button
                processSection.style.display = 'block';
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<div class="loading"></div> Processing...';
                
                // Reset all steps
                for(let i = 1; i <= 3; i++) {
                    const step = document.getElementById('step' + i);
                    step.className = 'agent-step';
                    document.getElementById('result' + i).innerHTML = '';
                }
                
                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    // Show step-by-step processing with delays
                    await processStepByStep(result);
                    
                } catch(error) {
                    updateStepStatus(1, 'failed', 'Error: ' + error.message);
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '🚀 Start Compliance Check';
                }
            });
            
            async function processStepByStep(result) {
                // Step 1: Extraction
                updateStepStatus(1, 'active', 'Processing document...');
                await sleep(1000);
                updateStepStatus(1, 'completed', `<strong>Extracted Text:</strong><br>${result.extracted}`);
                
                // Step 2: Matching
                await sleep(500);
                updateStepStatus(2, 'active', 'Analyzing compliance rules...');
                await sleep(1500);
                const matchText = `<strong>Compliance Analysis:</strong><br>
                    • Rules Found: ${result.matches.matches.join(', ')}<br>
                    • Compliance Score: ${result.matches.compliance_score}<br>
                    • Should Continue: ${result.matches.should_continue ? 'Yes' : 'No'}`;
                updateStepStatus(2, 'completed', matchText);
                
                // Step 3: Summary
                await sleep(500);
                if(result.status === 'completed') {
                    updateStepStatus(3, 'active', 'Generating compliance summary...');
                    await sleep(1000);
                    updateStepStatus(3, 'completed', `<strong>Final Summary:</strong><br>${result.summary}`);
                } else {
                    updateStepStatus(3, 'failed', `<strong>Process Stopped:</strong><br>${result.reason}<br>Compliance score too low to proceed.`);
                }
            }
            
            function updateStepStatus(stepNum, status, result) {
                const step = document.getElementById('step' + stepNum);
                const resultDiv = document.getElementById('result' + stepNum);
                
                step.className = 'agent-step ' + status;
                resultDiv.innerHTML = result;
            }
            
            function sleep(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }
        </script>
    </body>
    </html>
    """

@app.post("/process")
async def process_document(file: UploadFile = File(...), jurisdiction: str = Form(...)):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Initialize workflow
        workflow = ConditionalComplianceWorkflow()
        
        # Process the document
        result = workflow.run_workflow(tmp_file_path, jurisdiction)
        
        return result
        
    finally:
        # Clean up temporary file
        os.unlink(tmp_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)