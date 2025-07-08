# Open Integration Agent

An AI-powered data integration platform that automatically extracts and maps data from API documentation into unified ontologies.

## 🎯 Project Overview

This project explores the extent of generative AI's potential in generic data onboarding tasks. The system uses intelligent agents to handle integration needs from end-to-end, significantly reducing the manual effort required for enterprise data integration.

### The Challenge

We are trying to:

1. **Parse API Documentation**: Automatically read and understand API specifications from public documentation
2. **Map to Ontology**: Intelligently map API data to destination database schemas
3. **Ingest Data**: Programmatically extract and transform data from multiple platforms

## 🏗️ Current Architecture

### Backend (Python/FastAPI)
- **FastAPI**: Modern, fast web framework for building APIs
- **Health endpoints**: Basic API status and health checks
- **CORS configured**: Ready for frontend communication

### Frontend (React/TypeScript)
- **React 18**: Modern UI framework with TypeScript
- **Vite**: Fast build tool and development server
- **URL Input Form**: Clean interface for pasting API documentation URLs
- **Example URLs**: Shows supported platforms (Stripe, Shopify, HubSpot, QuickBooks)

## 🚀 Current Implementation

### ✅ What's Built
- **Project Foundation**: Basic FastAPI backend with health endpoints
- **Frontend Interface**: Clean React app with URL input form
- **Development Setup**: Hot reloading, TypeScript, and proper project structure
- **API Proxy**: Frontend can communicate with backend seamlessly
- **Intelligent API Parser**: Multi-model AI agent using Claude Sonnet 4 and Gemini Pro for comprehensive API documentation analysis
- **Multi-Platform Support**: Successfully tested with all 6 target platforms (Stripe, HubSpot, Shopify, QuickBooks, Zendesk, Jira)
- **Structured Data Extraction**: Extracts endpoints, authentication, rate limits, pagination, and integration notes
- **Ontology Mapper Agent**: Maps API endpoints/entities to ontology tables using name similarity
- **Data Ingestion Agent**: Generates and executes SDK code to extract data from APIs and ingest into Acho
- **End-to-End Pipeline**: Complete workflow from API parsing to data ingestion with error handling

### 🎯 Target Platforms

The system is designed to integrate with well-documented APIs including:

- **HubSpot** - CRM system
- **Stripe** - Payment processor  
- **Shopify** - E-commerce platform
- **QuickBooks** - Accounting software
- **Zendesk** - Customer support
- **Jira** - Project management

### ⚠️ HubSpot Integration Caveats

- **HubSpot integration works** with a valid Private App Token (PAT) from a production (non-developer, non-sandbox) portal.
- The PAT must have the correct scopes (e.g., `crm.objects.contacts.read`, `crm.objects.companies.read`, `crm.objects.deals.read`, etc.).
- The PAT must be active and from the same portal as the data you are accessing.
- Use the PAT in the `Authorization: Bearer <token>` header for all API calls.
- **Developer/test/sandbox portals may not work** with PATs for CRM v3 endpoints; these may require OAuth 2.0 instead.
- If you get authentication errors, double-check your portal type, token, and scopes.

## 🛠️ Technology Stack

### Backend
- **Python 3.12+**
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Anthropic Claude** - Primary AI model for API analysis
- **Google Gemini Pro** - Secondary AI model for large context analysis
- **BeautifulSoup** - HTML parsing and content extraction
- **Requests** - HTTP client for web scraping

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Axios** - HTTP client

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
npm install
# Set your API keys in .env file
echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here" > .env
echo "ACHO_TOKEN=your_acho_token_here" >> .env
echo "STRIPE_SK=your_stripe_secret_key_here" >> .env  # Optional: for Stripe API testing
echo "HUBSPOT_API_KEY=your_hubspot_api_key_here" >> .env  # Optional: for HubSpot API testing
echo "GOOGLE_API_KEY=your_google_api_key_here" >> .env  # Optional: for Gemini Pro
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The backend will run on `http://localhost:8000` and the frontend on `http://localhost:3000`.

## 🧪 Testing the Full Pipeline

Test the intelligent parser with any API documentation URL:

```bash
curl -X POST "http://localhost:8000/api/parse-doc" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.stripe.com/api"}'
```

Test the complete data ingestion pipeline:

```bash
# 1. Parse API documentation
curl -X POST "http://localhost:8000/api/parse-doc" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.stripe.com/api"}'

# 2. Map to ontology (returns mapping)
curl -X POST "http://localhost:8000/api/map-ontology" \
  -H "Content-Type: application/json" \
  -d '{"api_spec": {...}, "acho_token": "your_acho_token_here"}'

# 3. Ingest data (generates SDK and executes)
curl -X POST "http://localhost:8000/api/ingest-data" \
  -H "Content-Type: application/json" \
  -d '{"api_spec": {...}, "mapping": {...}}'
```

The frontend automatically chains all three endpoints for a complete integration workflow.

### 🤖 Multi-Model AI Architecture

The parser intelligently chooses the best AI model for each analysis:

- **Claude Sonnet 4**: Used for smaller content (< 10K chars) and when Gemini unavailable
- **Gemini Pro**: Used for large content (> 10K chars) with 1M+ token context window
- **Automatic Fallback**: Seamlessly switches between models based on content size and availability

**Benefits:**
- ✅ **Larger context windows** (50K chars vs 15K before)
- ✅ **More comprehensive extraction** of endpoints and entities
- ✅ **Better handling** of complex API documentation
- ✅ **Automatic model selection** for optimal performance

## 📝 About This Project

This project was created as a takehome assignment for **Aden**. The goal is to demonstrate how intelligent agents can automate complex data onboarding tasks that traditionally require significant manual effort.
