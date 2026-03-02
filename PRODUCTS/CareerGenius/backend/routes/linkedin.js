const express = require('express');
const OpenAI = require('openai');

const router = express.Router();
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Optimize LinkedIn profile
async function optimizeLinkedIn(resumeText, currentHeadline, currentSummary) {
  const prompt = `Optimize this LinkedIn profile based on the resume. Make it keyword-rich and engaging.

RESUME:
${resumeText}

${currentHeadline ? `CURRENT HEADLINE:\n${currentHeadline}\n\n` : ''}
${currentSummary ? `CURRENT SUMMARY:\n${currentSummary}\n\n` : ''}

Provide optimization in this JSON format:
{
  "headline": {
    "current": "${currentHeadline || 'Not provided'}",
    "optimized": "new headline with keywords (220 chars max)",
    "alternatives": ["alternative 1", "alternative 2"],
    "tips": ["headline tips"]
  },
  "summary": {
    "current": "${currentSummary || 'Not provided'}",
    "optimized": "compelling about/summary section (2000 chars max)",
    "keyElements": ["elements included"],
    "callToAction": "CTA at end"
  },
  "experience": {
    "optimizationTips": ["tips for each role"],
    "actionVerbs": ["strong verbs to use"],
    "metricsToAdd": ["specific metrics suggestions"]
  },
  "skills": {
    "topSkills": ["skill1", "skill2"],
    "skillsToAdd": ["additional skills to list"],
    "endorsementStrategy": "how to get endorsements"
  },
  "featured": {
    "contentIdeas": ["what to feature"],
    "projectsToHighlight": ["projects from resume"],
    "mediaSuggestions": ["types of media to add"]
  },
  "networking": {
    "connectionRequests": ["template messages"],
    "engagementStrategy": "how to engage with content",
    "groupsToJoin": ["suggested groups"]
  },
  "seo": {
    "keywords": ["keywords to include throughout profile"],
    "searchOptimization": "tips for appearing in searches"
  }
}`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: 'You are a LinkedIn profile optimization expert and personal branding specialist.' },
      { role: 'user', content: prompt }
    ],
    response_format: { type: 'json_object' },
    temperature: 0.4
  });

  return JSON.parse(response.choices[0].message.content);
}

// Generate LinkedIn posts/content
async function generateContent(resumeText, topic, contentType) {
  const prompt = `Generate LinkedIn content based on this professional background:

RESUME:
${resumeText}

TOPIC: ${topic}
CONTENT TYPE: ${contentType} (post/article/about section/connection request)

Provide in JSON format:
{
  "content": "the generated content",
  "hashtags": ["relevant", "hashtags"],
  "engagementTips": ["tips for engagement"],
  "bestPostingTime": "best time to post",
  "alternatives": ["alternative version 1", "alternative version 2"]
}`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: 'You are a LinkedIn content strategist.' },
      { role: 'user', content: prompt }
    ],
    response_format: { type: 'json_object' },
    temperature: 0.6
  });

  return JSON.parse(response.choices[0].message.content);
}

// LinkedIn optimization endpoint
router.post('/optimize', async (req, res) => {
  try {
    const { resumeText, currentHeadline, currentSummary } = req.body;
    
    if (!resumeText) {
      return res.status(400).json({ error: 'Resume text is required' });
    }

    const optimization = await optimizeLinkedIn(resumeText, currentHeadline, currentSummary);
    res.json(optimization);
  } catch (error) {
    console.error('LinkedIn optimization error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Generate content
router.post('/generate-content', async (req, res) => {
  try {
    const { resumeText, topic, contentType } = req.body;
    
    const content = await generateContent(resumeText, topic, contentType);
    res.json(content);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Connection request templates
router.post('/connection-templates', async (req, res) => {
  try {
    const { resumeText, targetRole, targetCompany, context } = req.body;
    
    const prompt = `Generate LinkedIn connection request templates for connecting with ${targetRole} at ${targetCompany}.
Context: ${context}

Candidate background: ${resumeText.substring(0, 500)}

Provide 5 different templates in JSON:
{
  "templates": [
    { "scenario": "...", "message": "...", "characterCount": number },
    ...
  ],
  "followUpStrategy": "...",
  "networkingTips": ["..."]
}`;

    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You are a LinkedIn networking expert.' },
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
