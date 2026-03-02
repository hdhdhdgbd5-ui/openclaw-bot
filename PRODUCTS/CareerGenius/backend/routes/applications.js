const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { format, parseISO, isAfter, isBefore, addDays } = require('date-fns');
const fs = require('fs').promises;
const path = require('path');

const router = express.Router();
const DATA_FILE = path.join(__dirname, '..', 'data', 'applications.json');

// Ensure data file exists
async function ensureDataFile() {
  try {
    await fs.access(DATA_FILE);
  } catch {
    await fs.mkdir(path.dirname(DATA_FILE), { recursive: true });
    await fs.writeFile(DATA_FILE, JSON.stringify([]));
  }
}

// Read all applications
async function readApplications() {
  await ensureDataFile();
  const data = await fs.readFile(DATA_FILE, 'utf-8');
  return JSON.parse(data);
}

// Write applications
async function writeApplications(applications) {
  await fs.writeFile(DATA_FILE, JSON.stringify(applications, null, 2));
}

// Get all applications
router.get('/', async (req, res) => {
  try {
    const { status, sortBy = 'appliedDate', order = 'desc' } = req.query;
    let applications = await readApplications();
    
    if (status) {
      applications = applications.filter(app => app.status === status);
    }
    
    applications.sort((a, b) => {
      const aVal = a[sortBy] || '';
      const bVal = b[sortBy] || '';
      return order === 'desc' 
        ? String(bVal).localeCompare(String(aVal))
        : String(aVal).localeCompare(String(bVal));
    });
    
    res.json(applications);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Add new application
router.post('/', async (req, res) => {
  try {
    const applications = await readApplications();
    
    const newApplication = {
      id: uuidv4(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      status: 'applied',
      ...req.body
    };
    
    applications.push(newApplication);
    await writeApplications(applications);
    
    res.status(201).json(newApplication);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update application
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const applications = await readApplications();
    
    const index = applications.findIndex(app => app.id === id);
    if (index === -1) {
      return res.status(404).json({ error: 'Application not found' });
    }
    
    applications[index] = {
      ...applications[index],
      ...req.body,
      updatedAt: new Date().toISOString()
    };
    
    await writeApplications(applications);
    res.json(applications[index]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Delete application
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    let applications = await readApplications();
    
    applications = applications.filter(app => app.id !== id);
    await writeApplications(applications);
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get dashboard stats
router.get('/stats/dashboard', async (req, res) => {
  try {
    const applications = await readApplications();
    
    const stats = {
      total: applications.length,
      byStatus: {},
      responseRate: 0,
      interviewRate: 0,
      offerRate: 0,
      thisWeek: 0,
      thisMonth: 0,
      averageResponseTime: null
    };
    
    const now = new Date();
    const oneWeekAgo = addDays(now, -7);
    const oneMonthAgo = addDays(now, -30);
    
    let responseTimes = [];
    let interviews = 0;
    let offers = 0;
    let responses = 0;
    
    applications.forEach(app => {
      // Count by status
      stats.byStatus[app.status] = (stats.byStatus[app.status] || 0) + 1;
      
      // Time-based counts
      const appliedDate = parseISO(app.appliedDate);
      if (isAfter(appliedDate, oneWeekAgo)) stats.thisWeek++;
      if (isAfter(appliedDate, oneMonthAgo)) stats.thisMonth++;
      
      // Response tracking
      if (['phone_screen', 'interview', 'final_round', 'offer', 'rejected'].includes(app.status)) {
        responses++;
        if (app.firstResponseDate) {
          responseTimes.push(
            Math.ceil((parseISO(app.firstResponseDate) - appliedDate) / (1000 * 60 * 60 * 24))
          );
        }
      }
      
      if (['interview', 'final_round', 'offer'].includes(app.status)) interviews++;
      if (app.status === 'offer') offers++;
    });
    
    if (applications.length > 0) {
      stats.responseRate = Math.round((responses / applications.length) * 100);
      stats.interviewRate = Math.round((interviews / applications.length) * 100);
      stats.offerRate = Math.round((offers / applications.length) * 100);
    }
    
    if (responseTimes.length > 0) {
      stats.averageResponseTime = Math.round(
        responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length
      );
    }
    
    // Pipeline funnel
    stats.pipeline = {
      applied: stats.byStatus.applied || 0,
      phoneScreen: stats.byStatus.phone_screen || 0,
      interview: (stats.byStatus.interview || 0) + (stats.byStatus.final_round || 0),
      offer: stats.byStatus.offer || 0
    };
    
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get reminders/follow-ups
router.get('/reminders/upcoming', async (req, res) => {
  try {
    const applications = await readApplications();
    const now = new Date();
    const threeDaysFromNow = addDays(now, 3);
    
    const reminders = applications
      .filter(app => {
        if (!app.followUpDate) return false;
        const followUp = parseISO(app.followUpDate);
        return isAfter(followUp, now) || isBefore(followUp, threeDaysFromNow);
      })
      .map(app => ({
        id: app.id,
        company: app.company,
        role: app.role,
        followUpDate: app.followUpDate,
        daysUntil: Math.ceil((parseISO(app.followUpDate) - now) / (1000 * 60 * 60 * 24)),
        status: app.status,
        action: app.followUpAction || 'Send follow-up email'
      }))
      .sort((a, b) => a.daysUntil - b.daysUntil);
    
    res.json(reminders);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
