from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import httpx
import json

app = FastAPI()

API_BASE_URL = "http://localhost:8000"

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Web3 Compliance Analyzer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            .form-section { margin-bottom: 30px; }
            textarea { width: 100%; height: 200px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; }
            select, input[type="text"] { padding: 8px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            button:disabled { background: #ccc; cursor: not-allowed; }
            .results { margin-top: 30px; }
            .job-info { background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 10px 0; }
            .status { padding: 5px 10px; border-radius: 3px; font-weight: bold; }
            .status.pending { background: #fff3cd; color: #856404; }
            .status.running { background: #cce5ff; color: #004085; }
            .status.completed { background: #d4edda; color: #155724; }
            .status.failed { background: #f8d7da; color: #721c24; }
            .result-content { background: #fff; padding: 15px; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px; white-space: pre-wrap; }
            .loading { display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #007bff; border-radius: 50%; animation: spin 1s linear infinite; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Web3 Compliance Analyzer</h1>

            <div class="form-section">
                <h3>📄 Submit Document for Compliance Analysis</h3>
                <form id="complianceForm">
                    <label for="identifier">Purchaser Identifier:</label><br>
                    <input type="text" id="identifier" name="identifier" value="web3_user_123" required><br><br>

                    <label for="region">Regulatory Region:</label><br>
                    <select id="region" name="region" required>
                        <option value="">Select Region</option>
                        <option value="EU">European Union (MiCA, GDPR)</option>
                        <option value="US">United States (SEC, CFTC)</option>
                        <option value="UK">United Kingdom (FCA)</option>
                        <option value="IN">India (PMLA, DPDP)</option>
                    </select><br><br>

                    <label>Document Input:</label><br>
                    <div style="margin: 10px 0;">
                        <input type="radio" id="text_input" name="input_type" value="text" checked>
                        <label for="text_input">Paste Text</label>
                        <input type="radio" id="file_input" name="input_type" value="file" style="margin-left: 20px;">
                        <label for="file_input">Upload File</label>
                    </div>

                    <div id="text_area">
                        <textarea id="document_text" name="document_text" placeholder="Paste your Web3 project document here (whitepaper, tokenomics, etc.)..." required></textarea><br><br>
                    </div>

                    <div id="file_area" style="display: none;">
                        <input type="file" id="document_file" name="document_file" accept=".pdf,.txt,.md,.docx"><br>
                        <small>Supported formats: PDF, TXT, MD, DOCX</small><br><br>
                    </div>

                    <button type="submit" id="submitBtn">🚀 Start Compliance Analysis</button>
                </form>
            </div>

            <div class="results" id="results" style="display: none;">
                <h3>📊 Analysis Results</h3>
                <div id="jobInfo"></div>
                <div id="resultContent"></div>
            </div>
        </div>

        <script>
            // Toggle input type
            document.querySelectorAll('input[name="input_type"]').forEach(radio => {
                radio.addEventListener('change', function() {
                    const textArea = document.getElementById('text_area');
                    const fileArea = document.getElementById('file_area');
                    const textInput = document.getElementById('document_text');
                    const fileInput = document.getElementById('document_file');

                    if (this.value === 'text') {
                        textArea.style.display = 'block';
                        fileArea.style.display = 'none';
                        textInput.required = true;
                        fileInput.required = false;
                    } else {
                        textArea.style.display = 'none';
                        fileArea.style.display = 'block';
                        textInput.required = false;
                        fileInput.required = true;
                    }
                });
            });

            document.getElementById('complianceForm').addEventListener('submit', async function(e) {
                e.preventDefault();

                const submitBtn = document.getElementById('submitBtn');
                const results = document.getElementById('results');

                let documentText = '';

                // Get document content
                const inputType = document.querySelector('input[name="input_type"]:checked').value;
                if (inputType === 'text') {
                    documentText = document.getElementById('document_text').value;
                } else {
                    const fileInput = document.getElementById('document_file');
                    if (!fileInput.files[0]) {
                        alert('Please select a file');
                        return;
                    }

                    // Read file content
                    documentText = await readFileContent(fileInput.files[0]);
                }

                if (!documentText.trim()) {
                    alert('Document content cannot be empty');
                    return;
                }

                // Prepare data
                const formData = {
                    identifier_from_purchaser: document.getElementById('identifier').value,
                    region: document.getElementById('region').value,
                    input_data: {
                        document_text: documentText
                    }
                };

                // Show loading
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<div class="loading"></div> Analyzing...';

                try {
                    // Start job
                    const startResponse = await fetch('/start_job', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });

                    const startResult = await startResponse.json();

                    if (startResult.status !== 'success') {
                        throw new Error(startResult.detail || 'Failed to start job');
                    }

                    const jobId = startResult.job_id;

                    // Show initial results
                    results.style.display = 'block';
                    updateJobInfo(startResult);

                    // Poll for status
                    await pollJobStatus(jobId);

                } catch(error) {
                    alert('Error: ' + error.message);
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '🚀 Start Compliance Analysis';
                }
            });

            async function pollJobStatus(jobId) {
                const maxPolls = 60; // 5 minutes max
                let polls = 0;

                while (polls < maxPolls) {
                    try {
                        const statusResponse = await fetch(`/status?job_id=${jobId}`);
                        const statusResult = await statusResponse.json();

                        updateJobInfo(statusResult);

                        if (statusResult.status === 'completed') {
                            displayResult(statusResult.result, statusResult.agent_results);
                            break;
                        } else if (statusResult.status === 'failed') {
                            displayResult('Analysis failed: ' + (statusResult.error || 'Unknown error'));
                            break;
                        }

                        await sleep(5000); // Wait 5 seconds
                        polls++;
                    } catch(error) {
                        console.error('Polling error:', error);
                        break;
                    }
                }

                if (polls >= maxPolls) {
                    updateJobInfo({ status: 'timeout', payment_status: 'unknown' });
                    displayResult('Analysis timed out. Please try again.');
                }
            }

            function updateJobInfo(data) {
                const jobInfo = document.getElementById('jobInfo');
                const statusClass = data.status || 'pending';

                jobInfo.innerHTML = `
                    <div class="job-info">
                        <strong>Job ID:</strong> ${data.job_id || 'N/A'}<br>
                        <strong>Status:</strong> <span class="status ${statusClass}">${data.status || 'pending'}</span><br>
                        <strong>Payment Status:</strong> <span class="status ${data.payment_status || 'pending'}">${data.payment_status || 'pending'}</span><br>
                        <strong>Test Mode:</strong> ${data.test_mode ? 'Yes' : 'No'}
                    </div>
                `;
            }

            function displayResult(result, agentResults) {
                const resultContent = document.getElementById('resultContent');

                let html = '';

                if (agentResults) {
                    html += '<h4>Agent Processing Results:</h4>';
                    if (agentResults.extraction) {
                        html += `<div class="result-content"><strong>📄 Document Extraction:</strong><br>${agentResults.extraction}</div>`;
                    }
                    if (agentResults.compliance_analysis) {
                        html += `<div class="result-content"><strong>🔍 Compliance Analysis:</strong><br>${agentResults.compliance_analysis}</div>`;
                    }
                    if (agentResults.summary) {
                        html += `<div class="result-content"><strong>📋 Final Summary:</strong><br>${agentResults.summary}</div>`;
                    }
                }

                if (result) {
                    html += '<h4>Final Result:</h4>';
                    if (typeof result === 'string') {
                        html += `<div class="result-content">${result}</div>`;
                    } else {
                        html += `<div class="result-content">${JSON.stringify(result, null, 2)}</div>`;
                    }
                }

                resultContent.innerHTML = html;
            }

            function readFileContent(file) {
                return new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = (e) => resolve(e.target.result);
                    reader.onerror = (e) => reject(new Error('Failed to read file'));
                    reader.readAsText(file);
                });
            }

            function sleep(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }
        </script>
    </body>
    </html>
    """

@app.post("/start_job")
async def start_job(request: Request):
    """Proxy to main API"""
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/start_job", json=data)
        return response.json()

@app.get("/status")
async def get_status(job_id: str):
    """Proxy to main API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/status", params={"job_id": job_id})
        return response.json()

if __name__ == "__main__":
    import uvicorn
    print("Starting Web3 Compliance Frontend at http://localhost:3000")
    print("Make sure the main API is running at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=3000)