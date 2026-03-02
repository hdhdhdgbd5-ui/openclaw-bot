const express = require('express');
const OpenAI = require('openai');

const router = express.Router();
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Generate salary negotiation scripts
async function generateNegotiationScripts(jobTitle, currentSalary, offerDetails, marketData) {
  const prompt = `Generate salary negotiation scripts and strategies.

POSITION: ${jobTitle}
CURRENT SALARY: ${currentSalary || 'Not disclosed'}
OFFER DETAILS: ${JSON.stringify(offerDetails)}
${marketData ? `MARKET DATA: ${JSON.stringify(marketData)}` : ''}

Provide comprehensive guidance in this JSON format:
{
  "marketContext": {
    "salaryRange": { "low": number, "median": number, "high": number },
    "yourPosition": "where offer sits in range",
    "negotiationLeverage": ["factors working in your favor"]
  },
  "scripts": {
    "initialCounter": {
      "email": "written counter offer email",
      "phone": "phone conversation script",
      "inPerson": "face-to-face negotiation script"
    },
    "scenarios": {
      "offerTooLow": {
        "approach": "how to handle",
        "script": "what to say",
        "justification": ["points to make"]
      },
      "offerAtExpectations": {
        "approach": "should you negotiate?",
        "script": "if yes, what to say"
      },
      "offerAboveExpectations": {
        "approach": "how to secure it",
        "additionalAsks": ["what else to negotiate"]
      },
      "noBudgetIncrease": {
        "alternativeAsks": ["non-salary items"],
        "script": "how to pivot"
      }
    }
  },
  "compensationPackage": {
    "baseSalary": { "target": number, "minimum": number, "walkAway": number },
    "equity": { "howToNegotiate": "...", "typicalRange": "..." },
    "bonus": { "signOn": "...", "performance": "..." },
    "benefits": ["PTO", "remote work", "professional development", "etc"],
    "perks": ["negotiable perks"]
  },
  "tactics": {
    "anchoring": { "description": "...", "script": "..." },
    "silence": { "description": "...", "whenToUse": "..." },
    "bundling": { "description": "...", "example": "..." },
    "deadlinePressure": { "howToHandle": "...", "script": "..." }
  },
  "commonMistakes": [
    { "mistake": "...", "whyItHurts": "...", "betterApproach": "..." }
  ],
  "emailTemplates": {
    "thankYou": "post-offer thank you",
    "counterOffer": "formal counter",
    "accepting": "accepting with enthusiasm",
    "declining": "graceful decline"
  }
}`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: 'You are a salary negotiation expert and executive coach.' },
      { role: 'user', content: prompt }
    ],
    response_format: { type: 'json_object' },
    temperature: 0.4
  });

  return JSON.parse(response.choices[0].message.content);
}

// Salary research
async function salaryResearch(jobTitle, location, experience, industry) {
  const prompt = `Provide salary research and market insights for:

ROLE: ${jobTitle}
LOCATION: ${location}
EXPERIENCE: ${experience} years
INDUSTRY: ${industry || 'General'}

Respond in JSON:
{
  "salaryRanges": {
    "percentile25": number,
    "median": number,
    "percentile75": number,
    "percentile90": number
  },
  "totalCompensation": {
    "base": number,
    "bonus": "typical %",
    "equity": "typical for level",
    "benefitsValue": number
  },
  "factors": {
    "increasing": ["factors that increase pay"],
    "decreasing": ["factors that decrease pay"]
  },
  "negotiationPoints": ["specific leverage points"],
  "marketTrends": "current market conditions",
  "relatedRoles": [
    { "title": "...", "salaryRange": "..." }
  ]
}`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: 'You are a compensation research specialist.' },
      { role: 'user', content: prompt }
    ],
    response_format: { type: 'json_object' },
    temperature: 0.3
  });

  return JSON.parse(response.choices[0].message.content);
}

// Negotiation endpoint
router.post('/negotiation-scripts', async (req, res) => {
  try {
    const { jobTitle, currentSalary, offerDetails, marketData } = req.body;
    
    if (!jobTitle) {
      return res.status(400).json({ error: 'Job title is required' });
    }

    const scripts = await generateNegotiationScripts(jobTitle, currentSalary, offerDetails, marketData);
    res.json(scripts);
  } catch (error) {
    console.error('Salary negotiation error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Salary research endpoint
router.post('/research', async (req, res) => {
  try {
    const { jobTitle, location, experience, industry } = req.body;
    
    if (!jobTitle) {
      return res.status(400).json({ error: 'Job title is required' });
    }

    const research = await salaryResearch(jobTitle, location, experience, industry);
    res.json(research);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Offer evaluation
router.post('/evaluate-offer', async (req, res) => {
  try {
    const { offerDetails, personalPriorities, marketData } = req.body;
    
    const prompt = `Evaluate this job offer comprehensively.

OFFER: ${JSON.stringify(offerDetails)}
PRIORITIES: ${JSON.stringify(personalPriorities)}
MARKET: ${JSON.stringify(marketData)}

Respond in JSON:
{
  "overallScore": 0-100,
  "financialAnalysis": {
    "comparedToMarket": "above/below/at market",
    "effectiveHourlyRate": number,
    "growthPotential": "assessment"
  },
  "strengths": ["offer strengths"],
  "concerns": ["areas of concern"],
  "dealBreakers": ["potential deal breakers"],
  "mustNegotiate": ["items to definitely negotiate"],
  "niceToHave": ["items to try for"],
  "decisionFramework": {
    "acceptIf": ["conditions"],
    "negotiateIf": ["conditions"],
    "declineIf": ["conditions"]
  },
  "questionsToAsk": ["clarifying questions"],
  "timeline": "recommended response timeline"
}`;

    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You are a career strategist and compensation expert.' },
        { role: 'user', content: prompt }
      ],
      response_format: { type: 'json_object' },
      temperature: 0.4
    });

    res.json(JSON.parse(response.choices[0].message.content));
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
