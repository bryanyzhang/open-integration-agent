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

### ⚠️ Stripe Integration 

- **Stripe integration works** with a valid secret API key (starts with `sk_`).
- Use the API key in the `Authorization: Bearer <your_stripe_secret_key>` header for all API calls.
- The base URL should be `https://api.stripe.com/v1/`.
- Stripe supports both test and live modes; use the appropriate key for your environment.
- All requests must be made over HTTPS.
- See [Stripe API Docs](https://docs.stripe.com/api) for more details.

### ⚠️ HubSpot Integration 

- **HubSpot integration works** with a valid Private App Token (PAT) from a production (non-developer, non-sandbox) portal.
- The PAT must have the correct scopes (e.g., `crm.objects.contacts.read`, `crm.objects.companies.read`, `crm.objects.deals.read`, etc.).
- The PAT must be active and from the same portal as the data you are accessing.
- Use the PAT in the `Authorization: Bearer <token>` header for all API calls.
- **Developer/test/sandbox portals may not work** with PATs for CRM v3 endpoints; these may require OAuth 2.0 instead.
- If you get authentication errors, double-check your portal type, token, and scopes.

### ⚠️ Shopify Integration 

- **Shopify integration works** with a valid Admin API access token and store domain.
- The access token must be generated from a custom/private app in your Shopify store.
- Use the token in the `X-Shopify-Access-Token` header for all Admin API calls.
- The base URL should be `https://{SHOPIFY_STORE_DOMAIN}/admin/api/2023-10/`.
- See [Shopify API Docs](https://shopify.dev/docs/api) for more details.

### ⚠️ QuickBooks Integration 

- **QuickBooks integration works** with a valid OAuth 2.0 access token and company ID.
- The access token must be generated via the OAuth 2.0 flow for your QuickBooks app.
- Use the token in the `Authorization: Bearer <token>` header for all API calls.
- The base URL should be `https://sandbox-quickbooks.api.intuit.com/v3/company/{companyId}/` (sandbox) or `https://quickbooks.api.intuit.com/v3/company/{companyId}/` (production).
- See [QuickBooks API Docs](https://developer.intuit.com/app/developer/qbo/docs/develop) for more details.

### ⚠️ Zendesk Integration 

- **Zendesk integration works** with either an API token (email/token) or OAuth 2.0 access token.
- For API token, use your Zendesk email and API token.
- For OAuth, use the access token in the `Authorization: Bearer <token>` header.
- The base URL should be `https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/`.
- See [Zendesk API Docs](https://developer.zendesk.com/api-reference/ticketing/introduction/) for more details.

### ⚠️ Jira Integration 

- **Jira integration works** with either an API token (email/token) or OAuth 2.0 access token.
- For API token, use your Atlassian email and API token.
- For OAuth, use the access token in the `Authorization: Bearer <token>` header.
- The base URL should be `https://{JIRA_DOMAIN}/rest/api/3/` (Basic) or `https://api.atlassian.com/ex/jira/{JIRA_CLOUD_ID}/rest/api/3/` (OAuth).
- See [Jira API Docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/#about) for more details.

### ⚠️ Ramp Integration

- **Ramp integration works** with a valid API key.
- Use the API key in the `Authorization: Bearer <your_ramp_api_key>` header for all API calls.
- The base URL should be `https://api.ramp.com/developer/v1/`.
- All requests must be made over HTTPS.
- See [Ramp API Docs](https://docs.ramp.com/developer-api/v1/overview/introduction) for more details.

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
- requirements.txt

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
npm install
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

# Set your API keys in .env file
echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here" > .env
echo "ACHO_TOKEN=your_acho_token_here" >> .env
echo "STRIPE_SK=your_stripe_secret_key_here" >> .env  # Optional: for Stripe API testing
echo "HUBSPOT_API_KEY=your_hubspot_api_key_here" >> .env  # Optional: for HubSpot API testing
echo "GOOGLE_API_KEY=your_google_api_key_here" >> .env  # Optional: for Gemini Pro
echo "SHOPIFY_ACCESS_TOKEN=your_shopify_access_token_here" >> .env  # For Shopify API
echo "SHOPIFY_STORE_DOMAIN=your-store.myshopify.com" >> .env  # Your Shopify store domain
echo "QBO_ACCESS_TOKEN=your_quickbooks_oauth_access_token_here" >> .env  # For QuickBooks API
echo "QBO_COMPANY_ID=your_quickbooks_company_id_here" >> .env  # Your QuickBooks company ID
echo "QBO_ENV=sandbox" >> .env  # 'sandbox' or 'production'
echo "ZENDESK_EMAIL=your_email@domain.com" >> .env
echo "ZENDESK_API_TOKEN=your_zendesk_api_token_here" >> .env
echo "ZENDESK_SUBDOMAIN=your_subdomain" >> .env # (Optional for OAuth)
echo "ZENDESK_OAUTH_TOKEN=your_zendesk_oauth_token_here" >> .env
echo "JIRA_EMAIL=your_email@domain.com" >> .env
echo "JIRA_API_TOKEN=your_jira_api_token_here" >> .env
echo "JIRA_DOMAIN=your-domain.atlassian.net" >> .env
echo "JIRA_CLOUD_ID=your_jira_cloud_id_here" >> .env  # For OAuth 2.0
echo "JIRA_OAUTH_TOKEN=your_jira_oauth_token_here" >> .env  # For OAuth 2.0
echo "JIRA_AUTH_METHOD=basic" >> .env  # or 'oauth'
echo "RAMP_API_KEY=your_ramp_api_key_here" >> .env