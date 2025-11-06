# Format-A Python Backend

This is the Python backend repository for the Format-A IEEE Paper Generator application. It provides document processing capabilities using Python libraries like python-docx and ReportLab.

## Architecture

This repository works in conjunction with the main Format-A application:
- **Main App**: format-a.vercel.app (React frontend + Node.js API)
- **Python Backend**: format-a-python.vercel.app (Python document processing)

## Features

- IEEE-formatted document generation (DOCX)
- PDF generation and conversion
- Document preview generation
- Cross-origin API support for main application

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   # Copy .env.example to .env.local and configure
   cp .env.example .env.local
   ```

3. Test database connectivity:
   ```bash
   python test-db-connection.py
   ```

4. Run locally with Vercel CLI:
   ```bash
   vercel dev --listen 3001
   ```

5. Test endpoints:
   - http://localhost:3001/api/health - Health check with database status
   - http://localhost:3001/api/test-simple - Simple functionality test
   - http://localhost:3001/api/document-generator - IEEE document generation

## API Endpoints

- `/api/test-python` - Health check endpoint
- `/api/document-generator` - IEEE document generation
- `/api/docx-generator` - DOCX file generation
- `/api/pdf-generator` - PDF file generation
- `/api/health` - Backend status monitoring

## Environment Variables

Required environment variables:
- `DATABASE_URL` - Neon PostgreSQL connection string
- `JWT_SECRET` - JWT token validation secret
- `VITE_GOOGLE_CLIENT_ID` - Google authentication client ID

## Deployment

This repository deploys automatically to Vercel as a Python-only project. The main application calls these endpoints via cross-origin requests.

## Dependencies

- python-docx==1.1.2 - Word document generation
- reportlab==4.2.5 - PDF generation
- Pillow==10.1.0 - Image processing
- psycopg2-binary==2.9.9 - PostgreSQL connectivity
- PyJWT==2.8.0 - JWT token validation