# Poker Points v2 — Collaborative Session Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build real-time collaborative poker planning sessions where users create a session, invite participants via link, conduct multi-round voting with hidden votes + reveal, and assign final values to FigJam stickies.

**Architecture:** Backend (Node.js + Express + Socket.io) manages sessions and real-time vote broadcast. Plugin (TypeScript) provides UI for creating sessions, voting, and assigning values to stickies. All work on DEV branch, master untouched.

**Tech Stack:** Node.js, Express.js, Socket.io, TypeScript, Webpack, Vercel (free tier), FigJam Plugin API

---

## File Structure

### Backend (New)
```
backend/
├── package.json              (Express, Socket.io, cors, nodemon)
├── server.js                 (Express app + Socket.io setup)
├── vercel.json               (Vercel serverless config)
├── .env.example              (environment variables template)
└── api/
    └── sessions.js           (REST endpoints: POST /sessions, GET /sessions/:id, DELETE)
```

### Plugin (Modified)
```
├── code.tsx                  (add session UI + Socket.io client)
├── code.js                   (compiled, auto-generated)
├── ui.html                   (add session screens/modals)
└── manifest.json             (update if permissions needed)
```

### Documentation
```
docs/
├── LOCAL_SETUP.md            (how to run plugin + backend locally)
└── superpowers/
    └── specs/
        └── 2026-04-16-poker-points-v2-design.md  (already written)
```

---

## Implementation Tasks

### Task 1: Backend Setup & Dependencies

**Files:**
- Create: `backend/package.json`
- Create: `backend/.env.example`
- Create: `backend/vercel.json`

- [ ] **Step 1: Create backend/package.json**

```json
{
  "name": "poker-points-backend",
  "version": "1.0.0",
  "description": "Backend for Poker Points FigJam plugin",
  "main": "server.js",
  "scripts": {
    "dev": "nodemon server.js",
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "socket.io": "^4.6.1",
    "cors": "^2.8.5",
    "dotenv": "^16.0.3"
  },
  "devDependencies": {
    "nodemon": "^2.0.22"
  }
}
```

- [ ] **Step 2: Create backend/.env.example**

```
PORT=3001
FIGMA_API_KEY=your_figma_api_key_here
SESSION_EXPIRY_MINUTES=60
```

- [ ] **Step 3: Create backend/vercel.json**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "server.js",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "server.js"
    }
  ]
}
```

- [ ] **Step 4: Commit**

```bash
cd backend
npm install
git add package.json .env.example vercel.json
git commit -m "feat: initialize backend project structure"
```

---

### Task 2: Backend — Express App & Socket.io Setup

**Files:**
- Create: `backend/server.js`

- [ ] **Step 1: Write failing test (mock Socket.io connection)**

Create `backend/test/server.test.js`:

```javascript
const io = require('socket.io-client');
const http = require('http');
const express = require('express');

test('client can connect to server', (done) => {
  const app = express();
  const server = http.createServer(app);
  const socket = io.connect('http://localhost:3001', {
    reconnection: false
  });

  socket.on('connect', () => {
    expect(socket.connected).toBe(true);
    socket.disconnect();
    done();
  });
});
```

- [ ] **Step 2: Create backend/server.js with Express + Socket.io**

```javascript
require('dotenv').config();
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());

// In-memory session storage
const sessions = new Map();

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// REST API endpoints
const sessionsRouter = require('./api/sessions')(sessions);
app.use('/api', sessionsRouter);

// Socket.io connection handling
io.on('connection', (socket) => {
  console.log(`Client connected: ${socket.id}`);

  socket.on('join-session', (data) => {
    const { sessionId, userId, userName } = data;
    const session = sessions.get(sessionId);
    if (session) {
      socket.join(sessionId);
      session.participants.push({ userId, userName, socketId: socket.id });
      io.to(sessionId).emit('session-joined', {
        userId,
        userName,
        participantCount: session.participants.length
      });
    }
  });

  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`);
  });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = { app, server, io };
```

- [ ] **Step 3: Run server locally and verify it starts**

```bash
cd backend
npm install
node server.js
# Expected: "Server running on port 3001"
```

- [ ] **Step 4: Commit**

```bash
git add backend/server.js
git commit -m "feat: set up Express + Socket.io server"
```

---

### Task 3: Backend — REST API for Session Management

**Files:**
- Create: `backend/api/sessions.js`

- [ ] **Step 1: Write test for REST endpoints**

Create `backend/test/api.test.js`:

```javascript
const request = require('supertest');
const express = require('express');

test('POST /api/sessions creates new session', async () => {
  const res = await request(app).post('/api/sessions').send({
    createdBy: 'user123',
    title: 'Sprint Planning'
  });

  expect(res.status).toBe(201);
  expect(res.body).toHaveProperty('sessionId');
  expect(res.body).toHaveProperty('joinLink');
});

test('GET /api/sessions/:sessionId returns session', async () => {
  const res = await request(app).get('/api/sessions/abc123');
  expect(res.status).toBe(200);
  expect(res.body).toHaveProperty('participants');
});

test('DELETE /api/sessions/:sessionId ends session', async () => {
  const res = await request(app).delete('/api/sessions/abc123');
  expect(res.status).toBe(200);
});
```

- [ ] **Step 2: Create backend/api/sessions.js**

```javascript
const express = require('express');
const { v4: uuidv4 } = require('uuid');

module.exports = (sessions) => {
  const router = express.Router();

  // POST /api/sessions — create new session
  router.post('/sessions', (req, res) => {
    const { createdBy, title = 'Estimation Session' } = req.body;
    const sessionId = uuidv4().slice(0, 8);
    
    const session = {
      sessionId,
      createdBy,
      title,
      createdAt: Date.now(),
      status: 'active',
      participants: [{ userId: createdBy, userName: 'Creator' }],
      rounds: [],
      lastActivityAt: Date.now(),
      expiresAt: Date.now() + (60 * 60 * 1000) // 1 hour
    };

    sessions.set(sessionId, session);

    res.status(201).json({
      sessionId,
      joinLink: `${process.env.PLUGIN_URL || 'http://localhost:3000'}?session=${sessionId}`
    });
  });

  // GET /api/sessions/:sessionId — get session state
  router.get('/sessions/:sessionId', (req, res) => {
    const session = sessions.get(req.params.sessionId);
    if (!session) {
      return res.status(404).json({ error: 'Session not found' });
    }
    res.status(200).json(session);
  });

  // DELETE /api/sessions/:sessionId — end session
  router.delete('/sessions/:sessionId', (req, res) => {
    const deleted = sessions.delete(req.params.sessionId);
    if (!deleted) {
      return res.status(404).json({ error: 'Session not found' });
    }
    res.status(200).json({ message: 'Session ended' });
  });

  return router;
};
```

- [ ] **Step 3: Update backend/server.js to use sessions API**

Update the sessions router import:
```javascript
const sessionsRouter = require('./api/sessions')(sessions);
app.use('/api', sessionsRouter);
```

- [ ] **Step 4: Test endpoints with curl or Postman**

```bash
curl -X POST http://localhost:3001/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"createdBy":"user1","title":"Sprint Planning"}'
# Expected: 201 with sessionId
```

- [ ] **Step 5: Commit**

```bash
git add backend/api/sessions.js
git commit -m "feat: add REST API for session creation/management"
```

---

### Task 4: Backend — Socket.io Events for Voting

**Files:**
- Modify: `backend/server.js`

- [ ] **Step 1: Add vote casting event handler**

```javascript
socket.on('cast-vote', (data) => {
  const { sessionId, roundId, userId, value } = data;
  const session = sessions.get(sessionId);
  if (!session) return;

  const round = session.rounds.find(r => r.roundId === roundId);
  if (!round) return;

  // Remove previous vote by same user if exists
  round.votes = round.votes.filter(v => v.userId !== userId);
  
  // Add new vote
  round.votes.push({
    userId,
    value,
    timestamp: Date.now()
  });

  // Broadcast vote count to all in session
  io.to(sessionId).emit('vote-cast', {
    voteCount: round.votes.length,
    totalParticipants: session.participants.length
  });

  session.lastActivityAt = Date.now();
});

socket.on('reveal-votes', (data) => {
  const { sessionId, roundId } = data;
  const session = sessions.get(sessionId);
  if (!session) return;

  const round = session.rounds.find(r => r.roundId === roundId);
  if (!round) return;

  round.revealed = true;

  // Calculate average
  const total = round.votes.reduce((sum, v) => sum + (typeof v.value === 'number' ? v.value : 0), 0);
  const average = round.votes.length > 0 ? (total / round.votes.length).toFixed(2) : 0;

  io.to(sessionId).emit('votes-revealed', {
    votes: round.votes,
    average: parseFloat(average)
  });
});

socket.on('start-round', (data) => {
  const { sessionId, stickyTitle, stickyNotes, stickyId, scheme } = data;
  const session = sessions.get(sessionId);
  if (!session) return;

  const roundId = uuidv4().slice(0, 8);
  const round = {
    roundId,
    stickyId,
    stickyTitle,
    stickyNotes,
    scheme,
    votes: [],
    revealed: false
  };

  session.rounds.push(round);
  io.to(sessionId).emit('round-started', { roundId, stickyTitle });
});

socket.on('assign-value', (data) => {
  const { sessionId, roundId, value, stickyId } = data;
  const session = sessions.get(sessionId);
  if (!session) return;

  const round = session.rounds.find(r => r.roundId === roundId);
  if (!round) return;

  round.selectedValue = value;
  round.assignedAt = Date.now();

  io.to(sessionId).emit('value-assigned', {
    stickyId,
    value,
    roundId
  });

  session.lastActivityAt = Date.now();
});

socket.on('end-session', (data) => {
  const { sessionId } = data;
  sessions.delete(sessionId);
  io.to(sessionId).emit('session-ended', { reason: 'user-ended' });
});
```

- [ ] **Step 2: Test Socket.io events locally**

Create test client:
```javascript
const io = require('socket.io-client');
const socket = io('http://localhost:3001');

socket.on('connect', () => {
  socket.emit('join-session', {
    sessionId: 'test123',
    userId: 'user1',
    userName: 'Alice'
  });
});
```

- [ ] **Step 3: Commit**

```bash
git add backend/server.js
git commit -m "feat: add Socket.io event handlers for voting"
```

---

### Task 5: Plugin — Add Socket.io Client & Session UI Structure

**Files:**
- Modify: `code.tsx`
- Modify: `ui.html`

- [ ] **Step 1: Install Socket.io client**

```bash
npm install socket.io-client
```

- [ ] **Step 2: Update code.tsx to initialize Socket.io client**

Add at top of file:
```typescript
import { io } from 'socket.io-client';

let socket: any = null;
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:3001';

function initSocket() {
  if (!socket) {
    socket = io(BACKEND_URL, {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5
    });
  }
  return socket;
}
```

- [ ] **Step 3: Update ui.html to add session screens**

Replace body with:
```html
<body>
  <div id="app">
    <!-- Sessions Tab -->
    <div id="sessions-tab" class="tab">
      <h2>Estimation Sessions</h2>
      <button id="start-session">Start New Session</button>
      <input id="join-code" placeholder="Paste session code to join" />
      <div id="active-sessions"></div>
    </div>

    <!-- Voting Screen -->
    <div id="voting-screen" class="tab" style="display:none;">
      <div id="session-header">
        <h3 id="sticky-title"></h3>
        <p id="sticky-notes"></p>
      </div>
      <div id="scheme-selector">
        <label>Scheme: <select id="scheme-select"></select></label>
        <button id="edit-scheme">✏ Edit</button>
      </div>
      <div id="vote-buttons"></div>
      <div id="vote-status">Waiting for votes...</div>
      <button id="reveal-button">Reveal Votes</button>
      <div id="vote-results" style="display:none;">
        <div id="votes-list"></div>
        <div id="average"></div>
        <button id="assign-button">Assign Value</button>
      </div>
      <button id="next-button">Next Sticky</button>
      <button id="end-session">End Session</button>
    </div>

    <!-- Estimation Tab (existing) -->
    <div id="estimation-tab" class="tab">
      <!-- Keep existing content -->
    </div>

    <!-- Modals -->
    <div id="start-session-modal" class="modal" style="display:none;">
      <input id="session-title" placeholder="Session title (optional)" />
      <button id="create-session-btn">Create Session</button>
    </div>

    <div id="select-sticky-modal" class="modal" style="display:none;">
      <select id="sticky-select"><option>Load stickies...</option></select>
      <button id="new-sticky-btn">New Sticky</button>
    </div>

    <div id="new-sticky-modal" class="modal" style="display:none;">
      <input id="new-sticky-title" placeholder="Sticky title" />
      <textarea id="new-sticky-notes" placeholder="Notes (optional)"></textarea>
      <button id="create-sticky-btn">Create & Vote</button>
    </div>
  </div>

  <style>
    .tab { padding: 16px; }
    .modal { border: 1px solid #ccc; padding: 16px; margin: 8px 0; }
    button { padding: 8px; margin: 4px; }
    #vote-buttons { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 16px 0; }
    .vote-btn { padding: 12px; cursor: pointer; border: 1px solid #999; }
    .vote-btn.selected { background: #0066ff; color: white; }
  </style>
</body>
```

- [ ] **Step 4: Commit**

```bash
git add package.json code.tsx ui.html
git commit -m "feat: add Socket.io client and session UI structure"
```

---

### Task 6: Plugin — Session Creation & Join Logic

**Files:**
- Modify: `code.tsx`

- [ ] **Step 1: Add session creation handler**

```typescript
async function createSession(title: string) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        createdBy: figma.currentUser.id,
        title: title || 'Estimation Session'
      })
    });
    const { sessionId, joinLink } = await response.json();
    
    // Store session ID and join socket
    currentSessionId = sessionId;
    const socket = initSocket();
    socket.emit('join-session', {
      sessionId,
      userId: figma.currentUser.id,
      userName: figma.currentUser.name
    });

    // Show voting screen
    showVotingScreen();
    figma.ui.postMessage({ type: 'session-created', link: joinLink });
  } catch (error) {
    console.error('Failed to create session:', error);
  }
}

async function joinSession(sessionId: string) {
  try {
    const socket = initSocket();
    currentSessionId = sessionId;
    socket.emit('join-session', {
      sessionId,
      userId: figma.currentUser.id,
      userName: figma.currentUser.name
    });
    showVotingScreen();
  } catch (error) {
    console.error('Failed to join session:', error);
  }
}
```

- [ ] **Step 2: Add UI message handlers**

```typescript
figma.ui.onmessage = async (msg) => {
  if (msg.type === 'create-session') {
    createSession(msg.title);
  } else if (msg.type === 'join-session') {
    joinSession(msg.code);
  } else if (msg.type === 'cast-vote') {
    const socket = initSocket();
    socket.emit('cast-vote', {
      sessionId: currentSessionId,
      roundId: currentRoundId,
      userId: figma.currentUser.id,
      value: msg.value
    });
  } else if (msg.type === 'reveal-votes') {
    const socket = initSocket();
    socket.emit('reveal-votes', {
      sessionId: currentSessionId,
      roundId: currentRoundId
    });
  } else if (msg.type === 'assign-value') {
    const socket = initSocket();
    socket.emit('assign-value', {
      sessionId: currentSessionId,
      roundId: currentRoundId,
      value: msg.value,
      stickyId: msg.stickyId
    });
    // Write to sticky
    const sticky = figma.getNodeById(msg.stickyId) as StickyNode;
    if (sticky) {
      sticky.text = `${sticky.text} [${msg.value}pt]`;
    }
  } else if (msg.type === 'end-session') {
    const socket = initSocket();
    socket.emit('end-session', { sessionId: currentSessionId });
  }
};
```

- [ ] **Step 3: Commit**

```bash
git add code.tsx
git commit -m "feat: add session creation and join logic"
```

---

### Task 7: Plugin — Real-Time Updates via Socket.io

**Files:**
- Modify: `code.tsx`

- [ ] **Step 1: Add Socket.io event listeners**

```typescript
function setupSocketListeners() {
  const socket = initSocket();

  socket.on('session-joined', (data) => {
    figma.ui.postMessage({
      type: 'participant-joined',
      userName: data.userName,
      count: data.participantCount
    });
  });

  socket.on('vote-cast', (data) => {
    figma.ui.postMessage({
      type: 'vote-updated',
      voteCount: data.voteCount,
      totalParticipants: data.totalParticipants
    });
  });

  socket.on('votes-revealed', (data) => {
    figma.ui.postMessage({
      type: 'votes-revealed',
      votes: data.votes,
      average: data.average
    });
  });

  socket.on('value-assigned', (data) => {
    figma.ui.postMessage({
      type: 'value-assigned',
      stickyId: data.stickyId,
      value: data.value
    });
  });

  socket.on('round-started', (data) => {
    currentRoundId = data.roundId;
    figma.ui.postMessage({
      type: 'round-started',
      roundId: data.roundId,
      stickyTitle: data.stickyTitle
    });
  });

  socket.on('session-ended', (data) => {
    figma.ui.postMessage({
      type: 'session-ended',
      reason: data.reason
    });
  });

  socket.on('disconnect', () => {
    figma.ui.postMessage({ type: 'disconnected' });
  });

  socket.on('reconnect', () => {
    figma.ui.postMessage({ type: 'reconnected' });
  });
}

// Call on plugin load
setupSocketListeners();
```

- [ ] **Step 2: Commit**

```bash
git add code.tsx
git commit -m "feat: add Socket.io event listeners for real-time updates"
```

---

### Task 8: Plugin — Vote Display & Scheme Selection

**Files:**
- Modify: `ui.html`

- [ ] **Step 1: Add vote button generation in UI script**

```html
<script>
const schemes = {
  fibonacci: [1, 2, 3, 5, 8, 13, 21, '?'],
  modified: [0, 0.5, 1, 2, 3, 5, 8, 13, 20, 40, 100, '?'],
  tshirt: ['XS', 'S', 'M', 'L', 'XL', 'XXL']
};

let currentScheme = 'fibonacci';
let selectedVote = null;

function renderVoteButtons() {
  const container = document.getElementById('vote-buttons');
  container.innerHTML = '';
  const values = schemes[currentScheme];
  
  values.forEach(val => {
    const btn = document.createElement('button');
    btn.className = 'vote-btn';
    btn.textContent = val;
    btn.onclick = () => castVote(val);
    container.appendChild(btn);
  });
}

function castVote(value) {
  selectedVote = value;
  // Update UI
  document.querySelectorAll('.vote-btn').forEach(btn => {
    btn.classList.remove('selected');
  });
  event.target.classList.add('selected');
  
  // Send to plugin
  parent.postMessage({ pluginMessage: { type: 'cast-vote', value } }, '*');
}

// Populate scheme selector
const selector = document.getElementById('scheme-select');
Object.keys(schemes).forEach(key => {
  const option = document.createElement('option');
  option.value = key;
  option.textContent = key.charAt(0).toUpperCase() + key.slice(1);
  selector.appendChild(option);
});

selector.onchange = (e) => {
  currentScheme = e.target.value;
  renderVoteButtons();
};

renderVoteButtons();
</script>
```

- [ ] **Step 2: Add vote results display**

```html
<script>
window.onmessage = (event) => {
  const { type, votes, average, voteCount, totalParticipants } = event.data.pluginMessage || {};
  
  if (type === 'votes-revealed') {
    const resultsList = document.getElementById('votes-list');
    resultsList.innerHTML = '<h4>Votes:</h4>';
    votes.forEach(v => {
      resultsList.innerHTML += `<div>${v.userId}: ${v.value}</div>`;
    });
    
    document.getElementById('average').innerHTML = `<strong>Average: ${average}</strong>`;
    document.getElementById('vote-results').style.display = 'block';
  } else if (type === 'vote-updated') {
    document.getElementById('vote-status').textContent = 
      `${voteCount}/${totalParticipants} voted`;
  }
};
</script>
```

- [ ] **Step 3: Commit**

```bash
git add ui.html
git commit -m "feat: add vote button rendering and results display"
```

---

### Task 9: Plugin — Sticky Selection & Assignment

**Files:**
- Modify: `code.tsx`
- Modify: `ui.html`

- [ ] **Step 1: Add sticky list loading**

```typescript
async function loadStickies() {
  const selection = figma.currentPage.selection;
  const stickies = selection.filter(node => node.type === 'STICKY') as StickyNode[];
  
  figma.ui.postMessage({
    type: 'stickies-loaded',
    stickies: stickies.map(s => ({
      id: s.id,
      title: s.text.slice(0, 100),
      text: s.text
    }))
  });
}
```

- [ ] **Step 2: Add sticky selection UI (ui.html)**

```html
<script>
parent.postMessage({ pluginMessage: { type: 'load-stickies' } }, '*');

window.onmessage = (event) => {
  const { type, stickies } = event.data.pluginMessage || {};
  
  if (type === 'stickies-loaded') {
    const select = document.getElementById('sticky-select');
    select.innerHTML = '<option>Select a sticky</option>';
    stickies.forEach(s => {
      const option = document.createElement('option');
      option.value = s.id;
      option.textContent = s.title;
      select.appendChild(option);
    });
  }
};

document.getElementById('next-button').onclick = () => {
  const stickyId = document.getElementById('sticky-select').value;
  if (stickyId) {
    parent.postMessage({ pluginMessage: { 
      type: 'start-round', 
      stickyId,
      stickyTitle: 'Sticky Title'
    } }, '*');
  }
};
</script>
```

- [ ] **Step 3: Commit**

```bash
git add code.tsx ui.html
git commit -m "feat: add sticky selection and assignment workflow"
```

---

### Task 10: Documentation & Local Setup

**Files:**
- Create: `docs/LOCAL_SETUP.md`
- Modify: `README.md`

- [ ] **Step 1: Create docs/LOCAL_SETUP.md**

```markdown
# Local Development Setup

## Prerequisites
- Node.js 16+
- FigJam installed
- Git

## Backend Setup

1. Navigate to backend directory:
```bash
cd backend
npm install
```

2. Create .env file from .env.example:
```bash
cp .env.example .env
# Edit .env with your settings
PORT=3001
```

3. Start development server:
```bash
npm run dev
# Server should run on http://localhost:3001
```

## Plugin Setup

1. From root directory, build plugin:
```bash
npm install
npm run watch
```

2. In FigJam:
   - Main Menu → Plugins → Development → Import plugin from manifest
   - Select `manifest.json` from root
   - Run plugin

3. Configure plugin to connect to backend:
   - Set environment variable or hardcode `BACKEND_URL` in code.tsx
   - Default: `http://localhost:3001`

## Testing Workflow

1. Open FigJam with plugin loaded
2. Create session → share link
3. Open second browser window with same link
4. Cast votes, reveal, assign value
5. Check that value appears on sticky

## Troubleshooting

**Plugin won't connect to backend:**
- Verify backend is running on port 3001
- Check browser console for connection errors
- Verify CORS is enabled in server.js

**Socket.io connection fails:**
- Check firewall settings
- Try reloading plugin
- Restart backend server
```

- [ ] **Step 2: Update README.md with v2 features**

Add to main README:

```markdown
## v2 Features (Collaborative Sessions)

**New in v2:**
- Create poker planning sessions with unique link
- Real-time voting with hidden votes + reveal
- Multi-round estimation in single session
- Support for up to 80+ concurrent participants
- Customizable estimation schemes (Fibonacci, Modified Fibonacci, T-Shirt)
- Final values persist on FigJam stickies

**To use v2:**
1. Open plugin → Click "Start New Session"
2. Share the join link with team members
3. Participants join and vote on stickies
4. Reveal votes and see average
5. Assign final value to sticky
6. Continue with next sticky or end session

See LOCAL_SETUP.md for development instructions.
```

- [ ] **Step 3: Commit**

```bash
git add docs/LOCAL_SETUP.md README.md
git commit -m "docs: add local setup and v2 feature documentation"
```

---

### Task 11: Testing & QA

**Files:**
- Create: `backend/test/integration.test.js`

- [ ] **Step 1: Write integration test for full flow**

```javascript
const { io: ioClient } = require('socket.io-client');
const request = require('supertest');

describe('Poker Points v2 Integration', () => {
  let sessionId, socket1, socket2;

  beforeAll(async () => {
    // Create session
    const res = await request(app).post('/api/sessions').send({
      createdBy: 'user1',
      title: 'Test Session'
    });
    sessionId = res.body.sessionId;
  });

  test('Two users can join same session and vote', (done) => {
    socket1 = ioClient(`http://localhost:3001`);
    socket2 = ioClient(`http://localhost:3001`);

    let joined = 0;
    const onJoined = () => {
      joined++;
      if (joined === 2) {
        // Both joined, start voting
        socket1.emit('cast-vote', {
          sessionId,
          roundId: 'round1',
          userId: 'user1',
          value: 5
        });
        socket2.emit('cast-vote', {
          sessionId,
          roundId: 'round1',
          userId: 'user2',
          value: 8
        });
      }
    };

    socket1.on('session-joined', onJoined);
    socket2.on('session-joined', onJoined);

    socket1.on('vote-cast', (data) => {
      expect(data.voteCount).toBeGreaterThan(0);
    });

    socket1.emit('join-session', {
      sessionId,
      userId: 'user1',
      userName: 'Alice'
    });
    socket2.emit('join-session', {
      sessionId,
      userId: 'user2',
      userName: 'Bob'
    });

    setTimeout(() => {
      socket1.disconnect();
      socket2.disconnect();
      done();
    }, 2000);
  });
});
```

- [ ] **Step 2: Run tests**

```bash
cd backend
npm test
# Expected: All integration tests pass
```

- [ ] **Step 3: Manual QA checklist**

- [ ] Create session from plugin UI
- [ ] Share link with second participant
- [ ] Both users join same session
- [ ] User 1 votes, User 2 sees "1/2 voted"
- [ ] User 2 votes, User 1 sees "2/2 voted"
- [ ] Click Reveal, both see all votes + average
- [ ] Click Assign, sticky gets final value
- [ ] Select next sticky, continue voting
- [ ] End session, votes are cleared
- [ ] Test with 3+ participants
- [ ] Test sticky selection from board
- [ ] Test custom scheme creation

- [ ] **Step 4: Commit test results**

```bash
git add backend/test/integration.test.js
git commit -m "test: add integration tests for voting flow"
```

---

### Task 12: Deployment Prep

**Files:**
- Create: `.env.production` (for Vercel)
- Update: `backend/package.json` (add build script)

- [ ] **Step 1: Add production build script**

Update `backend/package.json`:
```json
"scripts": {
  "dev": "nodemon server.js",
  "start": "node server.js",
  "build": "echo 'No build needed for Node runtime'"
}
```

- [ ] **Step 2: Create deployment checklist**

```
Deployment Checklist:

Before merging DEV → master:
- [ ] All integration tests pass locally
- [ ] QA checklist complete (12 items)
- [ ] Backend tested with 5+ concurrent users
- [ ] Plugin loads without errors in FigJam
- [ ] Socket.io connection stable under load
- [ ] Sticky assignment writes correct values
- [ ] Session cleanup on disconnect works
- [ ] Fallback to manual mode if backend down

Vercel Deployment:
- [ ] Push backend code to Vercel
- [ ] Set environment variables on Vercel dashboard
- [ ] Test production endpoint with plugin
- [ ] Verify Socket.io works over HTTPS
- [ ] Monitor logs for errors
```

- [ ] **Step 3: Commit**

```bash
git add backend/package.json
git commit -m "chore: prepare backend for Vercel deployment"
```

---

## Summary

This plan builds Poker Points v2 in 12 focused tasks:

1. **Backend setup** (dependencies, Vercel config)
2. **Express + Socket.io** server
3. **REST API** for session CRUD
4. **Socket.io voting events** (cast, reveal, assign)
5. **Plugin Socket.io client** + UI structure
6. **Session creation & join** logic
7. **Real-time updates** via Socket.io listeners
8. **Vote display** + scheme selection
9. **Sticky selection** & assignment workflow
10. **Documentation** & local setup guide
11. **Integration testing** + QA
12. **Deployment prep** for Vercel

**Branch:** All work on DEV branch. Master untouched until ready for release.

**Tech debt:** None intentionally introduced. Code follows existing patterns.

**Testing:** TDD approach per task. Full integration test before deployment.

**Deployment:** Free tier Vercel (no cost). Monitor for 1-hour session expiry + cleanup.
