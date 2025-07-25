# ChatPlusPlus Backend

A Walmart-level ChatGPT clone backend built with FastAPI and PostgreSQL.  
Manages user registration, login, and chat sessions via HTTP. Supports real-time large language model responses through WebSockets. Also allows PDF and DOCX uploads for enhanced interactions.

---

## Features

- User authentication with JWT  
- User registration and login management  
- Chat and message CRUD operations  
- Real-time LLM responses via WebSockets  
- PDF and DOCX file uploads  
- Integration with Groq Cloud service for large language models  
- Well-documented API endpoints with Swagger UI  

---

## Tech Stack

- **Backend Framework:** FastAPI  
- **Database:** PostgreSQL  
- **Authentication:** JSON Web Tokens (JWT)  
- **LLM Service:** Groq Cloud API  
- **Hosting:** Render (https://chatplusplus-backend.onrender.com)

---

## Getting Started

### Prerequisites

- Python 3.12.11  
- PostgreSQL database  
- `.env` file with the following variables:
  - `DATABASE_URL` – your PostgreSQL connection string  
  - `SECRET_KEY` – secret key for JWT token signing  
  - `FRONTEND_URL` – URL of your frontend app (for CORS)  
  - `GROQ_API_KEY` – API key for Groq Cloud LLM service  

### Installation

1. Clone the repository:
