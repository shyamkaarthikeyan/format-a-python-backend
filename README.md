# Format-A Python Backend

This is the Python backend for the Format-A application, deployed as Vercel serverless functions.

## 🚀 Features

- **Document Generation**: IEEE format papers with proper formatting
- **PDF and DOCX Creation**: Using ReportLab and python-docx
- **Database Integration**: Neon PostgreSQL with connection pooling
- **JWT Authentication**: Shared authentication with main Format-A app
- **CORS Support**: Configured for format-a.vercel.app cross-origin requests

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check with database connectivity |
| `/api/health-simple` | GET | Simple health check without database |
| `/api/test-simple` | GET | Basic functionality test |
| `/api/document-generator` | POST | IEEE document generation and preview |

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally with Vercel CLI
vercel dev --listen 3001

# Test endpoints
curl http://localhost:3001/api/health-simple
```

## 🔧 Environment Variables

Copy `.env.example` to `.env.local` and configure:

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://username:password@host:port/database

# Authentication (must match main Format-A app)
JWT_SECRET=your-jwt-secret-key
VITE_GOOGLE_CLIENT_ID=your-google-client-id

# Email Configuration
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-email-app-password

# Environment
NODE_ENV=production
```

## 🚀 Deployment

### Production Deployment
```bash
# Deploy to Vercel
vercel --prod

# Configure environment variables
vercel env add DATABASE_URL production
vercel env add JWT_SECRET production
# ... add other variables
```

### Git Integration Setup
This project needs to be connected to a Git repository for automatic deployments:

1. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Repository name: `format-a-python-backend`
   - Description: "Python backend for Format-A IEEE Paper Generator"
   - Set to Public or Private as needed
   - Click "Create repository"

2. **Connect Local Repository**:
   ```bash
   git remote add origin https://github.com/yourusername/format-a-python-backend.git
   git branch -M main
   git push -u origin main
   ```

3. **Connect Vercel to GitHub**:
   - Go to https://vercel.com/dashboard
   - Find your `format-a-python-backend` project
   - Go to Settings → Git
   - Connect to your GitHub repository
   - Enable automatic deployments

## 🧪 Testing

```bash
# Test local deployment
python test-local-deployment.py

# Test production deployment  
python test-deployment.py

# Test specific endpoints
python test-health-endpoint.py
python test-document-generator.py
```

## 📁 Project Structure

```
format-a-python-backend/
├── api/                          # Vercel serverless functions
│   ├── document-generator.py     # Document generation endpoint
│   ├── health.py                 # Health check with database
│   ├── health-simple.py          # Simple health check
│   └── test-simple.py            # Basic test endpoint
├── auth_utils.py                 # JWT authentication utilities
├── db_utils.py                   # Database connection utilities
├── ieee_generator_fixed.py       # IEEE document generator
├── requirements.txt              # Python dependencies
├── runtime.txt                   # Python version
├── vercel.json                   # Vercel configuration
└── .env.example                  # Environment variables template
```

## 🔗 Integration with Main App

This Python backend is designed to work alongside the main Format-A application:

- **Main App**: `https://format-a.vercel.app` (Node.js/React)
- **Python Backend**: `https://format-a-python-backend.vercel.app` (Python)

The frontend calls Python endpoints for document processing while using Node.js endpoints for authentication and core functionality.

## 🛡️ Security

- CORS configured for format-a.vercel.app domain
- JWT token validation using shared secret
- Environment variables encrypted in Vercel
- Database connections use SSL

## 📊 Monitoring

- Health endpoints for monitoring service status
- Database connectivity checks
- Environment variable validation
- Error logging and reporting

## 🔄 Current Status

✅ **Completed**:
- Python backend deployed to Vercel
- Environment variables configured
- CORS headers set up
- Document generation working
- Health check endpoints

⚠️ **Needs Setup**:
- Git repository connection for automatic deployments
- Custom domain configuration (optional)
- Production monitoring setup