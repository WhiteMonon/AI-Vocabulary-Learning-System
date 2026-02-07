# AI Vocabulary Learning System

A production-ready fullstack application for vocabulary learning using Spaced Repetition System (SRS) and AI-powered practice generation.

---

## 🚀 Core Features

### 🧠 Smart Vocabulary Management
- **AI-Enhanced Definitions**: Automatically fetch accurate definitions, synonyms, and context-aware examples.
- **Organization**: Group words into custom sets/categories.

### 📈 Spaced Repetition System (SRS)
- **Efficient Learning**: Optimized review schedules based on your performance.
- **Progress Tracking**: Visualize your learning curve and daily goals.

### 🤖 AI Practice & Interaction
- **Personalized Quizzes**: Generate dynamic quizzes based on your specific vocabulary list.
- **Smart Conversations**: Practice using your words in simulated real-world scenarios.
- **Multi-Provider Support**: Seamlessly switch between OpenAI, Groq, Gemini, or Local HF models.

### 🔒 Secure & Responsive
- **JWT Authentication**: Secure user accounts and data.
- **Modern UI**: Clean, responsive dashboard built with React and Tailwind CSS.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python (FastAPI), PostgreSQL (SQLModel), Redis, Alembic |
| **Frontend** | React, TypeScript, Vite, Tanstack Query, Tailwind CSS |
| **AI Integration** | LangChain, OpenAI/Groq/Gemini APIs |
| **DevOps** | Docker, Docker Compose |

---

## ⚙️ Installation & Setup

### Option 1: Quick Start with Docker (Recommended)

Make sure you have [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed.

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd AI-Vocabulary-Learning-System
   ```

2. **Configure environment variables**:
   Copy `.env.example` to `.env` and fill in your details (especially AI API keys).
   ```bash
   cp .env.example .env
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```
   The application will be available at `http://localhost`.

---

### Option 2: Manual Installation

#### Backend
1. Navigate to the backend directory: `cd backend`
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `alembic upgrade head`
5. Start the server: `./scripts/run.sh`

#### Frontend
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
