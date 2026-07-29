# 💊 AI-Powered Customer Complaint Management System

An AI-powered web application that helps manage pharmaceutical customer complaints by extracting structured information from complaint documents and text using Large Language Models (LLMs). The system simplifies complaint processing and provides an AI assistant for analysing complaint data.

## 🌐 Live Demo

**Frontend:** https://ai-pharma-complaint-management-syst-eight.vercel.app/

**Backend API:** https://complaint-management-api.onrender.com

**API Documentation:** https://complaint-management-api.onrender.com/docs

---

# Features

- Upload complaint documents in **PDF** and **DOCX** formats.
- Submit complaints by entering text manually.
- AI extracts structured complaint information from uploaded documents or text.
- Automatically stores extracted complaint details in a PostgreSQL database.
- View all stored complaints.
- Edit and update complaint information.
- AI chat assistant to answer questions related to a selected complaint.
- REST API built using FastAPI.
- Responsive React-based user interface.
- Production deployment using Vercel and Render.

---

# Tech Stack

## Frontend
- React
- Vite
- Redux Toolkit
- JavaScript
- CSS

## Backend
- FastAPI
- Python
- SQLAlchemy
- PostgreSQL

## AI
- Groq API
- LangGraph

## Deployment
- Vercel
- Render
- Render PostgreSQL

---

# Project Structure

```
complaint-management-system
│
├── frontend
├── backend
│   ├── app
│   ├── requirements.txt
│   └── .python-version
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/shrikantsul436-svg/ai-pharma-complaint-management-system.git
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

# Environment Variables

Create a `.env` file inside the backend folder.

```env
GROQ_API_KEY=your_api_key

DATABASE_URL=your_database_url

FRONTEND_ORIGIN=http://localhost:5173

GROQ_EXTRACTION_MODEL=llama-3.1-8b-instant

GROQ_REASONING_MODEL=llama-3.3-70b-versatile
```

---

# API Endpoints

## AI

- POST `/api/ai/ingest/document`
- POST `/api/ai/ingest/text`
- POST `/api/ai/chat`

## Complaints

- GET `/api/complaints`
- PUT `/api/complaints/{id}`

---

<img width="591" height="545" alt="Screenshot 2026-07-29 200758" src="https://github.com/user-attachments/assets/ebadfdc2-16e5-4d64-93e6-c26b0cddc018" />

<img width="772" height="901" alt="Screenshot 2026-07-29 200751" src="https://github.com/user-attachments/assets/3e5f2562-812c-494a-afdd-3d8e1ff23361" />


<img width="573" height="901" alt="Screenshot 2026-07-29 200739" src="https://github.com/user-attachments/assets/50f92c2f-aa01-47e1-bc36-f3ea1fe9bd2f" />


---

