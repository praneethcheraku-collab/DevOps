# Registration Application with Jenkins CI/CD

A full-stack registration application that stores user data in Excel files.

## 🚀 Features

- ✅ React frontend with modern UI
- ✅ Express.js REST API backend
- ✅ Excel file storage (.xlsx)
- ✅ Jenkins CI/CD pipeline
- ✅ Automated testing
- ✅ Production-ready build process

## 📋 Prerequisites

- Node.js (v16 or v18)
- npm
- Git
- Jenkins (optional, for CI/CD)

## 🏗️ Project Structure
```
registration-app/
├── backend/           # Express.js server
│   ├── server.js
│   └── package.json
├── frontend/          # React application
│   ├── src/
│   └── package.json
├── Jenkinsfile        # CI/CD pipeline
└── README.md
```

## 💻 Local Development

### Backend Setup
```cmd
cd backend
npm install
npm start
```
Server runs on: http://localhost:5000

### Frontend Setup
```cmd
cd frontend
npm install
npm start
```
Application opens on: http://localhost:3000

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Health check |
| GET | /api/registrations | Get all registrations |
| POST | /api/register | Add new registration |

## 📊 Data Storage

Registrations are stored in `backend/registrations.xlsx` with the following structure:
- ID
- Name
- Email
- Phone
- Date of Registration

## 🔄 Jenkins Pipeline

The CI/CD pipeline includes:
1. Code checkout
2. Dependency installation
3. Testing (backend & frontend)
4. Production build
5. Artifact archiving

## 🧪 Testing
```cmd
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test
```

## 🏭 Production Build
```cmd
cd frontend
npm run build
```

Build output: `frontend/build/`

## 📝 License

MIT

## 👨‍💻 Author

Praneeth