const express = require('express');
const OpenAI = require('openai');

const router = express.Router();
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Predict interview questions
async function predictQuestions(resumeText, jobDescription, interviewType) {
  const prompt = `Predict interview questions for this candidate based on their resume and the job description.

RESUME:
${resumeText}

JOB DESCRIPTION:
${jobDescription}

INTERVIEW TYPE: ${interviewType} (phone/screening/technical/behavioral/final)

Provide predictions in this JSON format:
{
  "predictedQuestions": {
    "technical": [
      { 
        "question": "...",
        "whyAsked": "reason this will be asked",
        "difficulty": "easy/medium/hard",
        "category": "coding/system design/behavioral/etc",
        "preparationTips": ["how to prepare"],
        "sampleAnswer": "strong example answer based on resume"
      }
    ],
    "behavioral": [
      {
        "question": "...",
        "starFormat": {
          "situation": "...",
          "task": "...",
          "action": "...",
          "result": "..."
        },
        "whatTheyWant": "what interviewer is looking for"
      }
    ],
    "situational": [
      {
        "question": "...",
        "approach": "how to answer",
        "keyPoints": ["points to cover"]
      }
    ],
    "companySpecific": [
      {
        "question": "...",
        "researchNeeded": "what to research about company"
      }
    ]
  },
  "resumeBasedQuestions": [
    "questions specific to gaps or transitions in resume"
  ],
  "questionsToAsk": [
    { "question": "...", "whenToAsk": "...", "whatItShows": "..." }
  ],
  "preparationPlan": {
    "priorityTopics": ["topics to focus on"],
    "timeAllocation": "how to allocate prep time",
    "mockInterviewScripts": ["practice scenarios"]
  }
}`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: 'You are an expert interview coach and former hiring manager.' },
      { role: 'user', content: prompt }
    ],
    response_format: { type: 'json_object' },
    temperature: 0.4
  });

  return JSON.parse(response.choices[0].message.content);
}

// Generate STAR format answers
async function generateStarAnswers(resumeText, questions) {
  const prompt = `Generate STAR format answers for these behavioral interview questions based on the resume:

RESUME:
${resumeText}

QUESTIONS:
${questions.map((q, i) => `${i + 1}. ${q}`).join('\n')}

Provide answers in JSON:
{
  "answers": [
    {
      "question": "...",
      "star": {
        "situation": "context (1-2 sentences)",
        "task": "your responsibility (1 sentence)",
        "action": "what YOU did (2-3 sentences, emphasize personal contribution)",
        "result": "outcome with metrics (1-2 sentences)"
      },
      "fullAnswer": "complete answer paragraph",
      "timeEstimate": "how long to speak",
      "deliveryTips": ["body language", "tone tips"]
    }
  ]
}`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: 'You are an expert interview coach specializing in behavioral questions.' },
      { role: 'user', content: prompt }
    ],
    response_format: { type: 'json_object' },
    temperature: 0.4
  });

  return JSON.parse(response.choices[0].message.content);
}

// Predict questions endpoint
router.post('/predict', async (req, res) => {
  try {
    const { resumeText, jobDescription, interviewType = 'all' } = req.body;
    
    if (!resumeText || !jobDescription) {
      return res.status(400).json({ error: 'Resume text and job description are required' });
    }

    const predictions = await predictQuestions(resumeText, jobDescription, interviewType);
    res.json(predictions);
  } catch (error) {
    console.error('Interview prediction error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Generate answers
router.post('/generate-answers', async (req, res) => {
  try {
    const { resumeText, questions } = req.body;
    
    if (!resumeText || !questions || !Array.isArray(questions)) {
      return res.status(400).json({ error: 'Resume text and questions array are required' });
    }

    const answers = await generateStarAnswers(resumeText, questions);
    res.json(answers);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Mock interview simulation
router.post('/mock-interview', async (req, res) => {
  try {
    const { resumeText, jobDescription, difficulty = 'medium', focus = 'mixed' } = req.body;
    
    const prompt = `Create a mock interview simulation.

Resume: ${resumeText.substring(0, 1000)}
Job: ${jobDescription.substring(0, 500)}
Difficulty: ${difficulty}
Focus: ${focus}

Generate in JSON:
{
  "interview": [
    {
      "sequence": 1,
      "type": "introduction/technical/behavioral/situational/closing",
      "question": "...",
      "followUps": ["potential follow-up questions"],
      "idealAnswer": "what a great answer includes",
      "commonMistakes": ["mistakes to avoid"],
      "scoreCriteria": ["what interviewers grade on"]
    }
  ],
  "evaluationRubric": {
    "technical": "criteria",
    "communication": "criteria",
    "culturalFit": "criteria"
  },
  "feedbackTemplate": "how to self-evaluate"
}`;

    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You create realistic mock interviews.' },
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
