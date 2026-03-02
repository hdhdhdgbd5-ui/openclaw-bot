const express = require('express');
const multer = require('multer');
const pdfParse = require('pdf-parse');
const mammoth = require('mammoth');
const OpenAI = require('openai');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs').promises;
const path = require('path');

const router = express.Router();
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowedTypes.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only PDF, DOC, DOCX, and TXT allowed.'));
    }
  }
});

// Parse resume from file
async function parseResume(buffer, mimetype, originalname) {
  const ext = path.extname(originalname).toLowerCase();
  let text = '';

  try {
    if (ext === '.pdf') {
      const data = await pdfParse(buffer);
      text = data.text;
    } else if (ext === '.docx') {
      const result = await mammoth.extractRawText({ buffer });
      text = result.value;
    } else if (ext === '.doc') {
      // For .doc files, we'd need a conversion service or library
      throw new Error('Legacy .doc format not supported. Please convert to .docx or PDF.');
    } else if (ext === '.txt') {
      text = buffer.toString('utf-8');
    }
  } catch (error) {
    console.error('Parse error:', error);
    throw new Error('Failed to parse resume: ' + error.message);
  }

  return text;
}

// AI Resume Scoring and Analysis
async function analyzeResume(resumeText) {
  const prompt = `Analyze this resume for ATS (Applicant Tracking System) optimization and overall quality. 
  
Resume Content:
${resumeText}

Provide a detailed analysis in this exact JSON format:
{
  "atsScore": 0-100,
  "overallScore": 0-100,
  "sections": {
    "contactInfo": { "present": true/false, "score": 0-100, "feedback": "..." },
    "summary": { "present": true/false, "score": 0-100, "feedback": "..." },
    "experience": { "present": true/false, "score": 0-100, "feedback": "..." },
    "education": { "present": true/false, "score": 0-100, "feedback": "..." },
    "skills": { "present": true/false, "score": 0-100, "feedback": "..." }
  },
  "keywordOptimization": {
    "score": 0-100,
    "strengths": ["..."],
    "missingKeywords": ["..."],
    "actionVerbs": ["..."]
  },
  "formatting": {
    "score": 0-100,
    "issues": ["..."],
    "suggestions": ["..."]
  },
  "improvements": [
    { "priority": "high/medium/low", "section": "...", "suggestion": "..." }
  ],
  "extractedData": {
    "name": "...",
    "email": "...",
    "phone": "...",
    "skills": ["..."],
    "jobTitles": ["..."],
    "yearsExperience": number
  }
}`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: 'You are an expert resume reviewer and ATS optimization specialist.' },
      { role: 'user', content: prompt }
    ],
    response_format: { type: 'json_object' },
    temperature: 0.3
  });

  return JSON.parse(response.choices[0].message.content);
}

// Optimize resume with AI
async function optimizeResume(resumeText, targetJobTitle, industry) {
  const prompt = `Optimize this resume for a ${targetJobTitle} position in the ${industry} industry.
Make it ATS-friendly, highlight relevant achievements with metrics, and use strong action verbs.

Original Resume:
${resumeText}

Provide the response in this JSON format:
{
  "optimizedResume": "full optimized resume text with proper formatting",
  "changesMade": [
    { "type": "added/removed/modified", "section": "...", "description": "..." }
  ],
  "keywordsAdded": ["..."],
  "atsImprovements": ["..."],
  "formattingTips": ["..."]
}`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: 'You are an expert resume writer and career coach.' },
      { role: 'user', content: prompt }
    ],
    response_format: { type: 'json_object' },
    temperature: 0.4
  });

  return JSON.parse(response.choices[0].message.content);
}

// Upload and analyze resume
router.post('/upload', upload.single('resume'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const resumeId = uuidv4();
    const resumeText = await parseResume(req.file.buffer, req.file.mimetype, req.file.originalname);
    
    // Save to temporary storage
    const dataDir = path.join(__dirname, '..', 'data');
    await fs.mkdir(dataDir, { recursive: true });
    await fs.writeFile(
      path.join(dataDir, `${resumeId}.json`),
      JSON.stringify({ text: resumeText, filename: req.file.originalname, uploadedAt: new Date() })
    );

    // Analyze with AI
    const analysis = await analyzeResume(resumeText);

    res.json({
      success: true,
      resumeId,
      filename: req.file.originalname,
      analysis
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get resume analysis
router.get('/analysis/:resumeId', async (req, res) => {
  try {
    const { resumeId } = req.params;
    const dataPath = path.join(__dirname, '..', 'data', `${resumeId}.json`);
    
    const data = await fs.readFile(dataPath, 'utf-8');
    const { text } = JSON.parse(data);
    
    const analysis = await analyzeResume(text);
    res.json(analysis);
  } catch (error) {
    res.status(404).json({ error: 'Resume not found' });
  }
});

// Optimize resume
router.post('/optimize/:resumeId', async (req, res) => {
  try {
    const { resumeId } = req.params;
    const { targetJobTitle, industry } = req.body;
    
    const dataPath = path.join(__dirname, '..', 'data', `${resumeId}.json`);
    const data = await fs.readFile(dataPath, 'utf-8');
    const { text } = JSON.parse(data);
    
    const optimization = await optimizeResume(text, targetJobTitle, industry);
    res.json(optimization);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Reanalyze with new text
router.post('/analyze-text', async (req, res) => {
  try {
    const { text } = req.body;
    if (!text || text.length < 50) {
      return res.status(400).json({ error: 'Resume text too short or missing' });
    }
    
    const analysis = await analyzeResume(text);
    res.json(analysis);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
