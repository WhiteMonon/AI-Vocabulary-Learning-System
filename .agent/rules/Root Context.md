---
trigger: always_on
---

PROJECT NAME: AI Vocabulary Learning System

GOAL:
Build production-ready fullstack app for vocabulary learning using SRS + AI practice generation.

STACK:
Backend:
- FastAPI
- PostgreSQL
- SQLModel
- Alembic
- Redis (optional)
- JWT Auth

Frontend:
- React
- Vite
- TypeScript
- Tanstack Query
- Tailwind

ARCHITECTURE RULES:
- Clean Architecture
- Service Layer pattern
- Repository pattern optional
- Strong typing everywhere
- Separation: API / Service / DB / AI

AI RULES:
- AI provider must be swappable
- Support:
  - OpenAI
  - Groq
  - Gemini
  - Local HF model

CODE RULES:
- Production ready
- Logging
- Error handling
- Validation
- Async when possible

OUTPUT RULE:
Always output full file content with file path header.

ENVIRONMENT & SECRET RULES:
- All API keys and secrets must be loaded from environment variables.
- Use .env file for local development only.
- Never hardcode API keys or secrets in source code.
- Never commit .env files.
- Never log secrets, tokens, or credentials.
