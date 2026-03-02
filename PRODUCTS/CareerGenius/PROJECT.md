# CareerGenius - Project Documentation

## Overview
CareerGenius is a full-stack AI-powered career optimization platform that replaces traditional career coaches with intelligent automation.

## Architecture

```
CareerGenius/
├── backend/          # Node.js API server
│   ├── routes/       # API endpoints
│   ├── middleware/   # Auth, validation
│   ├── utils/        # Helpers
│   └── data/         # Local storage
├── frontend/         # React SPA
│   ├── src/
│   │   ├── components/  # Reusable UI
│   │   ├── pages/       # Route pages
│   │   ├── stores/      # Zustand state
│   │   └── utils/       # Helpers
│   └── public/
└── shared/           # Common types/utils
```

## API Endpoints

### Resume
- `POST /api/resume/upload` - Upload and analyze resume
- `POST /api/resume/analyze-text` - Analyze pasted text
- `POST /api/resume/optimize/:id` - Optimize for specific job

### Jobs
- `POST /api/jobs/fit-score` - Calculate job fit
- `POST /api/jobs/parse-description` - Parse job details
- `POST /api/jobs/match-multiple` - Match multiple jobs

### Cover Letter
- `POST /api/cover-letter/generate` - Generate cover letter
- `POST /api/cover-letter/quick-generate` - Quick generation

### LinkedIn
- `POST /api/linkedin/optimize` - Optimize profile
- `POST /api/linkedin/generate-content` - Create content
- `POST /api/linkedin/connection-templates` - Network templates

### Interview
- `POST /api/interview/predict` - Predict questions
- `POST /api/interview/generate-answers` - Generate STAR answers
- `POST /api/interview/mock-interview` - Mock interview sim

### Salary
- `POST /api/salary/negotiation-scripts` - Generate scripts
- `POST /api/salary/research` - Market research
- `POST /api/salary/evaluate-offer` - Offer evaluation

### Applications
- `GET /api/applications` - List all
- `POST /api/applications` - Create
- `PUT /api/applications/:id` - Update
- `DELETE /api/applications/:id` - Delete
- `GET /api/applications/stats/dashboard` - Stats
- `GET /api/applications/reminders/upcoming` - Reminders

### Auth
- `POST /api/auth/register` - Sign up
- `POST /api/auth/login` - Sign in
- `GET /api/auth/me` - Current user

## AI Prompts

The platform uses carefully crafted prompts for:

1. **Resume Analysis** - ATS scoring, section evaluation
2. **Job Fit Calculation** - Skills matching, gap analysis
3. **Cover Letter Generation** - Tailored content creation
4. **LinkedIn Optimization** - Profile enhancement
5. **Interview Prediction** - Question forecasting
6. **Salary Negotiation** - Script generation

All prompts use GPT-4 with structured JSON output.

## Database Schema

### Users
```json
{
  "id": "uuid",
  "email": "string",
  "name": "string",
  "subscription": "free|pro|premium",
  "createdAt": "datetime"
}
```

### Applications
```json
{
  "id": "uuid",
  "userId": "uuid",
  "company": "string",
  "role": "string",
  "status": "enum",
  "appliedDate": "datetime",
  "salary": "string",
  "notes": "text"
}
```

## Security Considerations

1. All AI analysis happens server-side (API key protection)
2. File uploads limited to 10MB
3. Rate limiting on all endpoints
4. JWT tokens expire after 7 days
5. CORS restricted to known origins

## Performance

- React Query for efficient data fetching
- File storage uses in-memory + local JSON (scale to DB for production)
- AI calls cached where appropriate
- Lazy loading for route components

## Deployment Checklist

- [ ] Set production API URL
- [ ] Configure OpenAI API key
- [ ] Set JWT secret
- [ ] Enable rate limiting
- [ ] Configure CORS origins
- [ ] Set up monitoring/logging
- [ ] Enable HTTPS
- [ ] Test all features end-to-end
