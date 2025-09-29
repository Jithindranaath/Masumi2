from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
import tempfile
import os
from conditional_workflow import BuildingComplianceWorkflow

app = FastAPI()

@app.get("/")
async def home():
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Dashboard</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f0f0f0; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        h1 { color: #333; text-align: center; }
        .upload-box { border: 2px dashed #ccc; padding: 30px; text-align: center; margin: 20px 0; }
        input, select, button { padding: 10px; margin: 10px; font-size: 16px; }
        button { background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .results { margin-top: 30px; }
        .step { margin: 15px 0; padding: 15px; border-left: 4px solid #ddd; background: #f8f9fa; }
        .step.completed { border-left-color: #28a745; background: #d4edda; }
        .step.failed { border-left-color: #dc3545; background: #f8d7da; }
        .output { background: #fff; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏗️ Building Construction Compliance Dashboard</h1>
        
        <div class="upload-box">
            <h3>Upload Building Documents for Construction Approval</h3>
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" name="file" accept=".pdf,.txt" required><br>
                <select name="jurisdiction" required>
                    <option value="">Select Location</option>
                    <option value="India">India</option>
                    <option value="EU">Europe (EU)</option>
                    <option value="UK">United Kingdom</option>
                </select><br>
                <button type="submit">🏗️ Check Construction Approval</button>
            </form>
        </div>

        <div class="results" id="results" style="display:none;">
            <h3>Processing Results:</h3>
            <div id="step1" class="step">
                <strong>Step 1: Document Extraction</strong>
                <div id="output1" class="output"></div>
            </div>
            <div id="step2" class="step">
                <strong>Step 2: Compliance Matching</strong>
                <div id="output2" class="output"></div>
            </div>
            <div id="step3" class="step">
                <strong>Step 3: Summary Generation</strong>
                <div id="output3" class="output"></div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const results = document.getElementById('results');
            results.style.display = 'block';
            
            // Reset outputs
            document.getElementById('output1').innerHTML = 'Processing...';
            document.getElementById('output2').innerHTML = 'Waiting...';
            document.getElementById('output3').innerHTML = 'Waiting...';
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                // Show results
                document.getElementById('output1').innerHTML = result.extracted;
                document.getElementById('step1').className = 'step completed';
                
                document.getElementById('output2').innerHTML = 
                    'Matches: ' + result.matches.matches.join(', ') + 
                    '<br>Score: ' + result.matches.compliance_score +
                    '<br>Continue: ' + result.matches.should_continue;
                document.getElementById('step2').className = 'step completed';
                
                if(result.status === 'completed') {
                    document.getElementById('output3').innerHTML = result.summary;
                    document.getElementById('step3').className = 'step completed';
                } else {
                    document.getElementById('output3').innerHTML = 'Stopped: ' + result.reason;
                    document.getElementById('step3').className = 'step failed';
                }
                
            } catch(error) {
                document.getElementById('output1').innerHTML = 'Error: ' + error.message;
                document.getElementById('step1').className = 'step failed';
            }
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.post("/process")
async def process_file(file: UploadFile = File(...), jurisdiction: str = Form(...)):
    # Save uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Process with workflow
        workflow = BuildingComplianceWorkflow()
        result = workflow.run_workflow(tmp_file_path, jurisdiction)
        return result
    finally:
        os.unlink(tmp_file_path)

def find_free_port():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

if __name__ == "__main__":
    import uvicorn
    port = find_free_port()
    print(f"Starting server at http://localhost:{port}")
    print(f"Open your browser and go to: http://localhost:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port)