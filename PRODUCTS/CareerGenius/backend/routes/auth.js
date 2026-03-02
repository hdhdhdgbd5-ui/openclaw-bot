const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs').promises;
const path = require('path');

const router = express.Router();
const USERS_FILE = path.join(__dirname, '..', 'data', 'users.json');

const JWT_SECRET = process.env.JWT_SECRET || 'careergenius-secret-key';

// Ensure users file exists
async function ensureUsersFile() {
  try {
    await fs.access(USERS_FILE);
  } catch {
    await fs.mkdir(path.dirname(USERS_FILE), { recursive: true });
    await fs.writeFile(USERS_FILE, JSON.stringify([]));
  }
}

// Read users
async function readUsers() {
  await ensureUsersFile();
  const data = await fs.readFile(USERS_FILE, 'utf-8');
  return JSON.parse(data);
}

// Write users
async function writeUsers(users) {
  await fs.writeFile(USERS_FILE, JSON.stringify(users, null, 2));
}

// Register
router.post('/register', async (req, res) => {
  try {
    const { email, password, name } = req.body;
    
    if (!email || !password || !name) {
      return res.status(400).json({ error: 'Email, password, and name are required' });
    }
    
    const users = await readUsers();
    
    if (users.find(u => u.email === email)) {
      return res.status(400).json({ error: 'Email already registered' });
    }
    
    const hashedPassword = await bcrypt.hash(password, 10);
    
    const newUser = {
      id: uuidv4(),
      email,
      password: hashedPassword,
      name,
      createdAt: new Date().toISOString(),
      subscription: 'free', // free, basic, premium
      resumes: [],
      settings: {}
    };
    
    users.push(newUser);
    await writeUsers(users);
    
    const token = jwt.sign(
      { userId: newUser.id, email: newUser.email },
      JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    res.status(201).json({
      token,
      user: {
        id: newUser.id,
        email: newUser.email,
        name: newUser.name,
        subscription: newUser.subscription
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    const users = await readUsers();
    const user = users.find(u => u.email === email);
    
    if (!user || !await bcrypt.compare(password, user.password)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        subscription: user.subscription
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get current user
router.get('/me', async (req, res) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }
    
    const decoded = jwt.verify(token, JWT_SECRET);
    const users = await readUsers();
    const user = users.find(u => u.id === decoded.userId);
    
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    res.json({
      id: user.id,
      email: user.email,
      name: user.name,
      subscription: user.subscription,
      createdAt: user.createdAt
    });
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
});

module.exports = router;
