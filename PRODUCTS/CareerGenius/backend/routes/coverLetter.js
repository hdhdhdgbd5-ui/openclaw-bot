const express = require('express');
const OpenAI = require('openai');

const router = express.Router();
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Generate tailored cover letter
async function generateCoverLetter(resumeText, jobDescription, options = {}) {
  const { tone = 'professional', highlightProjects = [], companyResearch = '' } = options;
  
  const prompt = `Generate a compelling, tailored cover letter based on this resume and job description.

RESUME:
${resumeText}

JOB DESCRIPTION:
${jobDescription}

${companyResearch ? `COMPANY RESEARCH:\n${companyResearch}\n\n` : ''}
${highlightProjects.length > 0 ? `PROJECTS TO HIGHLIGHT:\n${highlightProjects.join('\n')}\n\n` : ''}

Requirements:
- Tone: ${tone}
- Opening hook that grabs attention
- 3-4 paragraphs max
- Connect specific experiences to job requirements
- Show enthusiasm for the company
- End with strong call to action
- ATS-friendly (avoid tables, headers, footers)
- Use professional but conversational language

Provide response in this JSON format:
{
  "coverLetter": "full cover letter text",
  "sections": {
    "opening": "opening paragraph",
    "body": ["paragraph 1", "paragraph 2"],
    "closing": "closing paragraph"
  },
  "keyPoints": ["main selling points covered"],
  "customizationTips": ["specific ways to personalize further"],
  "alternativeVersions": {
    "shorter": "condensed version (150 words)",
    "formal": "more formal version",
    "creative": "slightly creative version for startups"
  }
}`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: 'You are an expert cover letter writer and career coach.' },
      { role: 'user', content: prompt }
    ],
    response_format: { type: 'json_object' },
    temperature: 0.5
  });

  return JSON.parse(response.choices[0].message.content);
}

// Generate cover letter endpoint
router.post('/generate', async (req, res) => {
  try {
    const { resumeText, jobDescription, tone, highlightProjects, companyResearch } = req.body;
    
    if (!resumeText || !jobDescription) {
      return res.status(400).json({ error: 'Resume text and job description are required' });
    }

    const coverLetter = await generateCoverLetter(resumeText, jobDescription, {
      tone,
      highlightProjects,
      companyResearch
    });

    res.json(coverLetter);
  } catch (error) {
    console.error('Cover letter error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Quick cover letter (minimal inputs)
router.post('/quick-generate', async (req, res) => {
  try {
    const { 
      name, 
      currentRole, 
      yearsExperience, 
      keySkills, 
      achievement,
      jobTitle,
      companyName,
      whyInterested
    } = req.body;

    const prompt = `Generate a professional cover letter with these details:

Candidate: ${name}
Current Role: ${currentRole}
Experience: ${yearsExperience} years
Key Skills: ${keySkills.join(', ')}
Top Achievement: ${achievement}
Target Job: ${jobTitle} at ${companyName}
Why Interested: ${whyInterested}

Provide a compelling cover letter in JSON format:
{
  "coverLetter": "full text",
  "wordCount": number
}`;

    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You are a professional cover letter writer.' },
        { role: 'user', content: prompt }
      ],
      response_format: { type: 'json_object' },
      temperature: 0.5
    });

    res.json(JSON.parse(response.choices[0].message.content));
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
