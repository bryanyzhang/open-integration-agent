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

### 🎯 Target Platforms

The system is designed to integrate with well-documented APIs including:

- **HubSpot** - CRM system
- **Stripe** - Payment processor  
- **Shopify** - E-commerce platform
- **QuickBooks** - Accounting software
- **Zendesk** - Customer support
- **Jira** - Project management

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
# Set your API keys in .env file
echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here" > .env
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

## 🧪 Testing the API Parser and Ontology Mapper

Test the intelligent parser with any API documentation URL:

```bash
curl -X POST "http://localhost:8000/api/parse-doc" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.stripe.com/api"}'
```

Test the ontology mapping agent with a parsed API spec and ontology schema:

```bash
curl -X POST "http://localhost:8000/api/map-ontology" \
  -H "Content-Type: application/json" \
  -d '{
    "api_spec": {
      "endpoints": [
        {"path": "/api/users", "data_type": "users", "description": "Get all users"},
        {"path": "/api/orders", "data_type": "orders", "description": "Get all orders"}
      ],
      "data_models": [
        {"name": "users", "fields": ["id", "name", "email"]},
        {"name": "orders", "fields": ["id", "user_id", "total"]}
      ]
    },
    "ontology_schema": {
      "tables": [
        {"name": "users", "fields": ["id", "name", "email"]},
        {"name": "orders", "fields": ["id", "user_id", "total"]}
      ]
    }
  }'
```

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

### 🎯 Best Practices for Optimal Results

#### **1. Choose the Right Documentation URLs**
For best entity extraction, avoid overview pages

#### **2. Proven High-Yield URLs**
These URLs consistently extract 10+ entities:

**✅ Tested & Verified:**
- **Petstore API**: `https://petstore.swagger.io/` (17 entities)
- **JSONPlaceholder**: `https://jsonplaceholder.typicode.com/` (12 entities)
- **HubSpot Objects**: `https://developers.hubspot.com/docs/api/crm/objects` (10 entities)

**🔄 Target Platforms (Alternative URLs):**
- **Stripe**: `https://stripe.com/docs/api/charges`, `https://stripe.com/docs/api/customers`
- **Zendesk**: `https://developer.zendesk.com/api-reference/ticketing/introduction/`
- **Shopify**: `https://shopify.dev/docs/api/admin-rest`, `https://shopify.dev/docs/api/storefront`
- **QuickBooks**: `https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities`
- **Jira**: `https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/`

#### **3. Avoid These URL Types**
- ❌ **Overview pages** (usually only 3-5 entities)
- ❌ **Landing pages** (minimal endpoint information)
- ❌ **Authentication-only pages** (no endpoint listings)
- ❌ **Rate-limited or blocked pages** (403/429 errors)

## 📝 About This Project

This project was created as a takehome assignment for **Aden**. The goal is to demonstrate how intelligent agents can automate complex data onboarding tasks that traditionally require significant manual effort.

## 🧪 Running Unit Tests

Unit tests for the ontology mapping logic are included in `backend/test_ontology_mapper.py` and can be run with:

```bash
cd backend
pytest test_ontology_mapper.py
```

The ontology mapping agent uses Claude 3.5 Sonnet in production, but the unit tests mock the Claude API for fast, reliable testing. 