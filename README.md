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
python -m uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The backend will run on `http://localhost:8000` and the frontend on `http://localhost:3000`.

## 📝 About This Project

This project was created as a takehome assignment for **Aden**. The goal is to demonstrate how intelligent agents can automate complex data onboarding tasks that traditionally require significant manual effort. 