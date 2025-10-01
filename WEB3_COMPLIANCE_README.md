# Web3 Compliance Analysis System

## Overview

The Web3 Compliance Analysis System is an AI-powered platform designed to help blockchain and Web3 projects assess their regulatory compliance across multiple jurisdictions. Using CrewAI agents and OpenAI's GPT models, the system analyzes project documents (whitepapers, tokenomics, technical specifications) against current regulatory frameworks including MiCA (EU), SEC/CFTC (US), and FCA (UK) regulations.

The system provides comprehensive compliance scoring, risk assessments, and actionable roadmaps to help projects navigate the complex Web3 regulatory landscape.

## Agent Descriptions

The system employs three specialized AI agents, each with distinct roles and expertise:

### ExtractorAgent
- **Role**: Web3 Document Analyzer
- **Goal**: Extract and analyze content from Web3 project documents
- **Backstory**: Expert at parsing whitepapers, tokenomics, and Web3 documentation
- **Capabilities**:
  - PDF text extraction using PyPDF2
  - Document content parsing and structuring
  - Identification of key project elements (tokenomics, use cases, compliance features)
  - Preparation of documents for regulatory analysis

### MatcherAgent
- **Role**: Web3 Compliance Expert
- **Goal**: Analyze Web3 projects against regulatory requirements
- **Backstory**: Specialized in MiCA, SEC, FCA, and other Web3 regulatory frameworks
- **Capabilities**:
  - Jurisdiction-specific regulatory compliance assessment
  - AI-powered analysis using OpenAI GPT-4 or fallback keyword-based analysis
  - Compliance scoring (0-1 scale)
  - Risk level assessment (low/medium/high)
  - Launch readiness determination (70%+ compliance threshold)
  - Identification of missing compliance requirements

### SummarizerAgent
- **Role**: Web3 Compliance Advisor
- **Goal**: Provide comprehensive compliance roadmap and risk assessment
- **Backstory**: Expert at creating actionable compliance strategies for Web3 startups
- **Capabilities**:
  - Synthesis of analysis results into comprehensive roadmaps
  - Risk mitigation strategy development
  - Compliance checklist generation
  - Regulatory next-step recommendations
  - Actionable compliance improvement plans

## Usage Guidelines

### Prerequisites
- Python 3.8+
- OpenAI API key (for enhanced analysis)
- Masumi payment service credentials (for production use)

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure environment variables:
   ```
   OPENAI_API_KEY=your_openai_key
   PAYMENT_SERVICE_URL=your_masumi_url
   PAYMENT_API_KEY=your_payment_key
   TEST_MODE=true  # Set to false for production
   ```

### Running the System

#### Option 1: Run All Services
```bash
python run_all.py
```
This starts both the API server (port 8000) and web frontend (port 3000).

#### Option 2: Run Services Separately
```bash
# Terminal 1: Start API server
python main.py api

# Terminal 2: Start web frontend
python web3_frontend.py
```

### API Usage
The system provides a REST API following the Masumi API Standard (MIP-003).

**Start Analysis Job:**
```bash
curl -X POST "http://localhost:8000/start_job" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier_from_purchaser": "web3_user_123",
    "region": "EU",
    "input_data": {
      "document_text": "Your Web3 project document content here..."
    }
  }'
```

**Check Job Status:**
```bash
curl "http://localhost:8000/status?job_id=YOUR_JOB_ID"
```

### Web Frontend Usage
1. Open http://localhost:3000 in your browser
2. Enter a purchaser identifier
3. Select regulatory region (EU/US/UK)
4. Input document content (paste text or upload PDF/TXT/MD/DOCX)
5. Click "Start Compliance Analysis"
6. Monitor progress and view results

## Examples

### Example 1: DeFi Protocol Analysis (EU Jurisdiction)
**Input Document:**
```
Our DeFi protocol enables decentralized lending and borrowing of crypto assets.
Tokenomics: Utility token with governance features.
We implement KYC procedures for users.
```

**Expected Output:**
```json
{
  "found_compliance": ["KYC Procedures", "Token Classification"],
  "missing_compliance": ["MiCA Compliance Assessment", "GDPR Privacy Impact Assessment"],
  "compliance_score": 0.65,
  "ready_for_launch": false,
  "risk_level": "medium",
  "regulatory_frameworks": ["MiCA", "GDPR"],
  "analysis": "Found 2/7 Web3 compliance requirements. Risk level: medium"
}
```

### Example 2: NFT Marketplace (US Jurisdiction)
**Input Document:**
```
NFT marketplace for digital art trading.
Security token offering with Howey Test compliance.
Registered with SEC as securities exchange.
```

**Expected Output:**
```json
{
  "found_compliance": ["SEC Registration Status", "Howey Test Analysis"],
  "missing_compliance": ["CFTC Registration Status", "State Regulatory Compliance"],
  "compliance_score": 0.75,
  "ready_for_launch": true,
  "risk_level": "low",
  "regulatory_frameworks": ["SEC", "CFTC"],
  "analysis": "Found 4/6 Web3 compliance requirements. Risk level: low"
}
```

### Example 3: Crypto Payment Service (UK Jurisdiction)
**Input Document:**
```
Electronic money institution licensed by FCA.
AML compliance with Money Laundering Regulations 2017.
Payment services registration completed.
```

**Expected Output:**
```json
{
  "found_compliance": ["FCA Registration Status", "Money Laundering Regulations Compliance"],
  "missing_compliance": ["Financial Promotion Compliance"],
  "compliance_score": 0.8,
  "ready_for_launch": true,
  "risk_level": "low",
  "regulatory_frameworks": ["FCA", "Payment Services Regulations"],
  "analysis": "Found 5/6 Web3 compliance requirements. Risk level: low"
}
```

## Capabilities

### Core Features
- **Multi-Jurisdiction Support**: EU (MiCA/GDPR), US (SEC/CFTC), UK (FCA)
- **Document Processing**: PDF, TXT, MD, DOCX file support
- **AI-Powered Analysis**: OpenAI GPT-4 integration with fallback keyword analysis
- **Compliance Scoring**: Quantitative assessment (0-1 scale) with launch readiness
- **Risk Assessment**: Low/Medium/High risk categorization
- **Comprehensive Reporting**: Detailed compliance checklists and roadmaps

### Technical Capabilities
- **CrewAI Integration**: Multi-agent collaborative analysis
- **Payment Integration**: Masumi payment system for monetization
- **Asynchronous Processing**: Job queuing and status monitoring
- **Web Frontend**: User-friendly interface for document submission
- **REST API**: Programmatic access following industry standards
- **Logging**: Comprehensive logging with configurable levels

### Regulatory Frameworks Covered
- **EU**: MiCA, GDPR, AML Directive, Consumer Protection
- **US**: SEC, CFTC, FinRA, BSA, Howey Test
- **UK**: FCA, Money Laundering Regulations, Payment Services Regulations

## Limitations

### Technical Limitations
- **AI Dependency**: Requires OpenAI API key for optimal analysis
- **Fallback Accuracy**: Keyword-based analysis less accurate than AI
- **File Size Limits**: Large PDFs may cause processing delays
- **Network Dependency**: Requires internet for OpenAI API calls

### Regulatory Limitations
- **Jurisdiction Scope**: Currently limited to EU, US, UK
- **Regulatory Updates**: May not reflect very recent regulatory changes
- **Legal Disclaimer**: Not a substitute for professional legal advice
- **Compliance Threshold**: 70% score is a general guideline, not absolute

### Operational Limitations
- **Payment Required**: Production use requires Masumi payment integration
- **Test Mode Only**: Development/testing without payment verification
- **Single Analysis**: Each job processes one document at a time
- **No Historical Tracking**: No persistent storage of analysis history

### Performance Considerations
- **Processing Time**: AI analysis may take 30-60 seconds
- **API Rate Limits**: Subject to OpenAI API rate limits
- **Concurrent Jobs**: Limited by server resources
- **Memory Usage**: Large documents increase memory requirements

## API Reference

### Base URL
```
http://localhost:8000
```

### Authentication
No authentication required for basic endpoints. Payment verification handled via Masumi integration.

### Endpoints

#### POST /start_job
Initiates a Web3 compliance analysis job.

**Request Body:**
```json
{
  "identifier_from_purchaser": "string",
  "region": "EU" | "US" | "UK",
  "input_data": {
    "document_text": "string"
  }
}
```

**Response (Success):**
```json
{
  "status": "success",
  "job_id": "uuid",
  "blockchainIdentifier": "string",
  "agentIdentifier": "string",
  "test_mode": true|false
}
```

**Response (Test Mode):**
```json
{
  "status": "success",
  "job_id": "uuid",
  "test_mode": true,
  "message": "Job completed in test mode",
  "result": {...}
}
```

#### GET /status
Retrieves the status of a compliance analysis job.

**Parameters:**
- `job_id` (string, required): The job identifier

**Response:**
```json
{
  "job_id": "uuid",
  "status": "pending|running|completed|failed",
  "payment_status": "pending|completed|failed",
  "test_mode": true|false,
  "result": "string|object",
  "agent_results": {
    "extraction": "string",
    "compliance_analysis": "object",
    "summary": "string"
  }
}
```

#### GET /availability
Checks server availability and operational status.

**Response:**
```json
{
  "status": "available",
  "type": "masumi-agent",
  "message": "Server operational."
}
```

#### GET /input_schema
Returns the expected input schema for the /start_job endpoint.

**Response:**
JSON schema object defining the StartJobRequest model.

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### Error Responses
All endpoints may return standard HTTP error codes:
- `400`: Bad Request (invalid input)
- `404`: Not Found (job not found)
- `500`: Internal Server Error

Error response format:
```json
{
  "detail": "Error description"
}
```

### Web Frontend Endpoints
The web frontend proxies API calls and adds additional endpoints:

#### GET /
Serves the main web interface (HTML page).

#### POST /start_job (Frontend Proxy)
Proxies to main API /start_job endpoint.

#### GET /status (Frontend Proxy)
Proxies to main API /status endpoint.

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for AI analysis
- `PAYMENT_SERVICE_URL`: Masumi payment service URL
- `PAYMENT_API_KEY`: Masumi payment API key
- `AGENT_IDENTIFIER`: Unique agent identifier
- `NETWORK`: Blockchain network (e.g., "mainnet")
- `TEST_MODE`: Enable test mode (true/false)
- `PAYMENT_AMOUNT`: Payment amount in lovelace
- `PAYMENT_UNIT`: Payment unit (default: "lovelace")

### Test Mode
When `TEST_MODE=true`, the system bypasses payment verification and executes jobs immediately. This is useful for development and testing.

## Troubleshooting

### Common Issues
1. **OpenAI API Errors**: Check API key and quota
2. **Payment Failures**: Verify Masumi credentials
3. **File Upload Issues**: Ensure supported file formats
4. **Timeout Errors**: Large documents may need more processing time

### Logs
Check `logging_config.py` for log configuration. Logs are written to console and can be configured for file output.

### Support
For issues or questions:
1. Check the logs for error details
2. Verify environment configuration
3. Ensure all dependencies are installed
4. Test with simple documents first

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request

### Code Standards
- Follow PEP 8 Python style guide
- Add type hints for new functions
- Include docstrings for all public methods
- Write unit tests for new features

### Adding New Jurisdictions
1. Update `ComplianceAnalysisTool` in `agents/compliance_agents.py`
2. Add jurisdiction-specific requirements
3. Update fallback analysis logic
4. Test with sample documents

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This system provides automated analysis and should not be considered legal advice. Always consult with qualified legal professionals for regulatory compliance matters. The analysis is based on current regulatory frameworks and may not reflect the most recent changes.