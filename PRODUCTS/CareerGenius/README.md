# CareerGenius 🚀

**AI-Powered Resume & Career Optimization Platform**

CareerGenius is a comprehensive career optimization platform that helps job seekers land their dream jobs through AI-powered tools. From resume analysis and ATS optimization to interview preparation and salary negotiation, we've got you covered.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 1. Resume Analyzer
- Upload PDF, DOCX, or paste resume text
- AI-powered ATS compatibility scoring
- Detailed section-by-section analysis
- Keyword optimization suggestions
- Actionable improvement recommendations

### 2. Job Matcher
- Calculate fit scores for any job description
- Skills gap analysis
- Experience matching
- Personalized recommendations

### 3. Cover Letter Generator
- Auto-generate tailored cover letters
- Multiple tone options (professional, confident, enthusiastic)
- Company research integration
- Customizable based on specific achievements

### 4. LinkedIn Optimizer
- Headline optimization with alternatives
- About/Summary section enhancement
- Skills and endorsement strategies
- Connection request templates

### 5. Interview Prep
- AI-predicted questions based on resume + job description
- STAR format answer generation
- Technical question predictions
- Questions to ask the interviewer

### 6. Salary Negotiation
- Market salary research
- Negotiation scripts (email, phone, in-person)
- Scenario-based guidance
- Total compensation package analysis

### 7. Application Tracker
- Full CRM for job applications
- Status tracking (applied → offer)
- Pipeline analytics
- Follow-up reminders

## 🛠 Tech Stack

### Backend
- **Node.js** + **Express** - API server
- **OpenAI GPT-4** - AI analysis and generation
- **PDF-parse** + **Mammoth** - Document parsing
- **JWT** - Authentication
- **Winston** - Logging

### Frontend
- **React 18** - UI framework
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Query** - Data fetching
- **Framer Motion** - Animations
- **Recharts** - Data visualization

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- OpenAI API key
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/careergenius.git
cd careergenius
```

2. Install backend dependencies:
```bash
cd backend
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

4. Start the backend:
```bash
npm run dev
```

5. Install frontend dependencies (in a new terminal):
```bash
cd ../frontend
npm install
```

6. Start the frontend:
```bash
npm start
```

The application will be available at `http://localhost:3000`

## 📊 Deployment

### Backend (Railway/Render/Heroku)
1. Set environment variables:
   - `OPENAI_API_KEY`
   - `JWT_SECRET`
   - `NODE_ENV=production`

2. Deploy with your preferred platform

### Frontend (Vercel/Netlify)
```bash
cd frontend
npm run build
```

Deploy the `build` folder to your static hosting provider.

## 💰 Monetization

CareerGenius uses a freemium model:

- **Free**: 3 resume analyses/month, basic features
- **Pro ($29/month)**: Unlimited access to all features
- **Premium ($79/month)**: Plus 1-on-1 coaching, API access

## 🔒 Security

- JWT-based authentication
- Rate limiting on API endpoints
- Input validation and sanitization
- File upload size limits
- CORS configuration

## 📈 Roadmap

- [ ] Chrome extension for job board integration
- [ ] Mobile app (React Native)
- [ ] AI-powered job recommendation engine
- [ ] Resume builder with templates
- [ ] Recruiter marketplace
- [ ] Video interview practice

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the powerful GPT-4 API
- The React and Node.js communities
- All the job seekers who provided feedback

---

**Made with ❤️ for job seekers everywhere**
