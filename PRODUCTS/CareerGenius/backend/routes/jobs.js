const express = require('express');
const OpenAI = require('openai');

const router = express.Router();
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Calculate job fit score
async function calculateJobFit(resumeText, jobDescription) {
  const prompt = `Compare this resume with the job description and calculate a detailed fit score.

RESUME:
${resumeText}

JOB DESCRIPTION:
${jobDescription}

Analyze and respond in this exact JSON format:
{
  "overallFitScore": 0-100,
  "category": "excellent(85+)/good(70-84)/fair(50-69)/poor(<50)",
  "matching": {
    "skills": {
      "score": 0-100,
      "matched": ["skill1", "skill2"],
      "missing": ["required skill1", "required skill2"]
    },
    "experience": {
      "score": 0-100,
      "yearsRequired": number,
      "yearsCandidate": number,
      "relevantExperience": ["..."]
    },
    "education": {
      "score": 0-100,
      "requirements": "...",
      "candidateEducation": "..."
    }
  },
  "gapAnalysis": {
    "criticalGaps": ["must-have missing skills"],
    "niceToHaveGaps": ["preferred missing skills"],
    "experienceGap": "description of experience gaps"
  },
  "recommendations": {
    "quickWins": ["immediate improvements to mention"],
    "skillDevelopment": ["skills to learn"],
    "applicationStrategy": "how to position yourself"
  },
  "keywords": {
    "mustInclude": ["keywords to add to resume"],
    "found": ["keywords already present"]
  }
}`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: 'You are an expert recruiter and talent acquisition specialist.' },
      { role: 'user', content: prompt }
    ],
    response_format: { type: 'json_object' },
    temperature: 0.3
  });

  return JSON.parse(response.choices[0].message.content);
}

// Job fit endpoint
router.post('/fit-score', async (req, res) => {
  try {
    const { resumeText, jobDescription } = req.body;
    
    if (!resumeText || !jobDescription) {
      return res.status(400).json({ error: 'Both resume text and job description are required' });
    }

    const fitAnalysis = await calculateJobFit(resumeText, jobDescription);
    res.json(fitAnalysis);
  } catch (error) {
    console.error('Job fit error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Parse job description
router.post('/parse-description', async (req, res) => {
  try {
    const { jobDescription } = req.body;
    
    if (!jobDescription) {
      return res.status(400).json({ error: 'Job description is required' });
    }

    const prompt = `Parse this job description and extract structured information:

${jobDescription}

Respond in this JSON format:
{
  "title": "job title",
  "company": "company name if mentioned",
  "location": "location if mentioned",
  "employmentType": "full-time/part-time/contract/etc",
  "salaryRange": "salary if mentioned",
  "requiredSkills": ["skill1", "skill2"],
  "preferredSkills": ["skill1", "skill2"],
  "requiredExperience": "years or description",
  "educationRequirements": ["degree requirements"],
  "responsibilities": ["key responsibility 1", "key responsibility 2"],
  "benefits": ["benefit 1", "benefit 2"],
  "companyValues": ["value 1", "value 2"],
  "atsKeywords": ["important keywords for ATS"]
}`;

    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You are a job description parser.' },
        { role: 'user', content: prompt }
      ],
      response_format: { type: 'json_object' },
      temperature: 0.3
    });

    res.json(JSON.parse(response.choices[0].message.content));
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Match multiple jobs
router.post('/match-multiple', async (req, res) => {
  try {
    const { resumeText, jobDescriptions } = req.body; // jobDescriptions is array
    
    const results = await Promise.all(
      jobDescriptions.map(async (job, index) => {
        const fit = await calculateJobFit(resumeText, job.description);
        return {
          jobIndex: index,
          jobTitle: job.title || `Job ${index + 1}`,
          company: job.company || 'Unknown',
          ...fit
        };
      })
    );

    // Sort by score
    results.sort((a, b) => b.overallFitScore - a.overallFitScore);
    
    res.json({ matches: results });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
