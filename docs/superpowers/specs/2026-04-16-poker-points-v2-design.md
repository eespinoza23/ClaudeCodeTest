# Poker Points FigJam v2 — Multi-Round Collaborative Session Design

**Date:** 2026-04-16  
**Status:** Design approved, ready for implementation  
**Branch:** DEV (isolated from master/production)

---

## Overview

Transform Poker Points from individual sticky estimation tool to real-time collaborative poker planning session. Users create sessions, invite participants via link, conduct multi-round voting with hidden votes + reveal, and assign final values to FigJam stickies.

**Key constraints:**
- Data persists in FigJam only (final assigned values as sticky properties)
- Vote history deleted after session ends (privacy)
- Support 80+ concurrent users per session
- Free tier hosting (Vercel + Node backend)

---

## Architecture

### Frontend: Enhanced FigJam Plugin

**Tech stack:** TypeScript, existing webpack build, Socket.io client

**Components:**
1. **Sessions Tab** (new)
   - List active sessions user created/joined
   - "Start New Session" button
   - "Join Session" input (paste link or code)

2. **Voting Screen** (new)
   - Sticky title + optional notes
   - **Scheme selector** (Fibonacci, Modified Fibonacci, T-Shirt, or custom)
   - Vote buttons (dynamic based on selected scheme)
   - Edit scheme button (add/remove/modify values, persists for session)
   - Reveal button (after all vote or manual trigger)
   - Vote display (count before reveal, all votes after)
   - Average calculation + display
   - "Assign to Sticky" button (writes final value to FigJam)
   - "Next Sticky" / "End Session" buttons

3. **Estimation Tab** (existing)
   - Keep manual estimation mode unchanged
   - Can exist alongside session mode

**Modals:**
- Start session (optional title + description)
- Select/Create sticky (dropdown to select or form to create new)
- End session confirmation

**Real-time updates via Socket.io:**
- Vote count updates as participants vote
- Instant reveal broadcast
- Average recalculated server-side
- User join/leave notifications

---

### Backend: Vercel + Node.js

**Tech stack:** Express.js + Socket.io, in-memory session storage, auto-cleanup

**Responsibilities:**
- Session lifecycle (create → active → ended)
- Real-time vote broadcast
- Vote aggregation + average calculation
- Session auto-expiry (1hr inactivity)
- Participant management (join/leave tracking)

**Session storage:** In-memory only (no database). Persisted during session, deleted on end or expiry.

**Deployment:** Vercel free tier (`vercel.json` config included)

---

## Data Model

### Session (Backend In-Memory)

```json
{
  "sessionId": "abc123",
  "createdBy": "userId",
  "createdAt": 1713292800000,
  "status": "active",
  "participants": [
    { "userId": "user1", "userName": "Alice", "joinedAt": 1713292800000 }
  ],
  "rounds": [
    {
      "roundId": "round1",
      "stickyId": "figma_sticky_123",
      "stickyTitle": "As a user, I can login",
      "stickyNotes": "Support SSO + password reset",
      "scheme": {
        "name": "Fibonacci",
        "values": [1, 2, 3, 5, 8, 13, 21, "?"]
      },
      "votes": [
        { "userId": "user1", "value": 5, "timestamp": 1713292810000 },
        { "userId": "user2", "value": 8, "timestamp": 1713292812000 }
      ],
      "revealed": true,
      "selectedValue": 5,
      "assignedAt": 1713292830000
    }
  ],
  "lastActivityAt": 1713292830000,
  "expiresAt": 1713379230000
}
```

### Vote (Ephemeral, Cleared After Round)

```json
{
  "userId": "string",
  "sessionId": "string",
  "roundId": "string",
  "value": 5,
  "timestamp": 1713292810000
}
```

**Lifecycle:** Created on vote cast → broadcast to all participants → deleted after round completion or session end.

### FigJam Sticky Properties

Final assigned value stored as sticky property (existing mechanism, extended):

```json
{
  "estimatedValue": 5,
  "estimatedAt": "2026-04-16T12:00:00Z",
  "sessionId": "abc123",
  "estimatedBy": "userId"
}
```

---

## Real-Time Flow

### 1. Create Session

**Plugin UI:** User clicks "Start New Session"  
**Modal:** Enter optional title + description  
**Backend:** Generate unique session ID, return join link  
**Result:** Session created, user auto-joined as creator

### 2. Join Session

**Plugin UI:** User pastes session link or code  
**Backend:** Validate session, add user to participants  
**Broadcast:** Notify all participants of new user  
**Result:** User sees live voting screen, current round state

### 3. Select Scheme (First Round)

**Plugin UI:** Choose scheme (Fibonacci, Modified Fibonacci, T-Shirt, custom)  
**Option:** Edit scheme values if needed  
**Backend:** Store selected scheme for round  
**Result:** Scheme persists across participants + rounds unless changed

### 4. Vote (Hidden)

**Plugin UI:** Click value from selected scheme  
**Backend:** Store vote, broadcast count (not values)  
**Plugin UI:** Show "3 votes cast, 2 waiting..."  
**Result:** Vote hidden until reveal

### 5. Reveal

**Plugin UI:** "Reveal" button (manual or auto-trigger after timeout)  
**Backend:** Broadcast all votes + calculated average  
**Plugin UI:** Display all votes + average  
**Result:** Participants see voting distribution

### 6. Assign Value

**Plugin UI:** User clicks "Assign X to Sticky"  
**Plugin → FigJam:** Write final value as sticky property  
**Backend:** Clear round votes, mark round complete  
**Plugin UI:** Show success, offer next action  
**Result:** Value persisted in FigJam sticky

### 7. Next Action

**Option A: Next Sticky**
- Modal: Select existing sticky from board OR create new
- If new: enter title + optional notes
- Backend: Start new round
- Plugin: Return to vote screen

**Option B: End Session**
- Confirmation modal
- Backend: Delete session + all votes
- Plugin: Return to Sessions tab
- All participants disconnected

---

## API & WebSocket Events

### REST Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/sessions` | Create new session, return sessionId + join link |
| GET | `/sessions/:sessionId` | Get session state (for rejoin) |
| DELETE | `/sessions/:sessionId` | End session, cleanup votes |

### WebSocket Events (Socket.io)

**Plugin → Backend:**
- `join-session` → `{ sessionId, userId, userName }`
- `cast-vote` → `{ sessionId, roundId, userId, value }`
- `reveal-votes` → `{ sessionId, roundId }`
- `assign-value` → `{ sessionId, roundId, value, stickyId }`
- `start-round` → `{ sessionId, stickyTitle, stickyNotes, stickyId? }`
- `end-session` → `{ sessionId }`

**Backend → All Connected Clients:**
- `session-joined` → `{ userId, userName, participantCount }`
- `vote-cast` → `{ voteCount, totalParticipants }`
- `votes-revealed` → `{ votes: [{ userId, value }], average }`
- `value-assigned` → `{ stickyId, value, roundId }`
- `round-started` → `{ roundId, stickyTitle, stickyNotes }`
- `participant-left` → `{ userId, userName, participantCount }`
- `session-ended` → `{ reason: "user-ended" | "expired" }`
- `error` → `{ message }`

---

## Error Handling & Edge Cases

### Network Issues

**Plugin disconnects mid-vote:**
- Auto-reconnect with exponential backoff
- Preserve vote locally, re-cast on reconnect
- Display "reconnecting..." status + retry button
- If reconnect fails, show fallback (manual mode)

**Session expires (1hr inactivity):**
- Backend marks session as expired
- Broadcast to all participants: "Session expired"
- Plugin returns to Sessions tab
- All votes deleted

### Session Issues

**Late voter arrives after reveal:**
- Backend returns full vote history immediately
- Plugin displays all votes + average on join

**User votes twice per round:**
- Backend rejects second vote (validation)
- Plugin shows error: "You already voted"

**Sticky not found in FigJam:**
- Plugin validates sticky exists before assignment
- Show error: "Sticky no longer exists, select another"

**Backend down:**
- Plugin detects connection timeout
- Offer fallback: switch to manual estimation mode
- Alert user: "Session unavailable, use offline mode"

### Data Validation

- Vote value must exist in current scheme
- Sticky ID must be valid FigJam object
- User cannot vote twice per round
- Session ID must be active (not expired)
- Participant limit: none (scale to 80+)

---

## File Structure (DEV Branch)

```
poker-points-figjam/
├── code.tsx                 (enhanced plugin, session UI)
├── code.js                  (compiled from code.tsx)
├── ui.html                  (existing + new session screens)
├── manifest.json            (updated permissions if needed)
├── package.json             (deps unchanged for plugin)
├── webpack.config.js        (unchanged)
│
├── backend/                 (NEW)
│   ├── package.json         (Express, Socket.io, cors)
│   ├── server.js            (Express + Socket.io entry)
│   ├── vercel.json          (Vercel deployment config)
│   └── api/
│       └── sessions.js      (REST endpoints for session CRUD)
│
├── docs/
│   ├── ARCHITECTURE.md       (high-level overview, kept updated)
│   └── LOCAL_SETUP.md        (how to run locally + test)
│
└── .gitignore               (backend/.env, node_modules, build artifacts)
```

---

## Testing Strategy

### Unit Tests
- Vote aggregation (average calculation)
- Session state transitions
- WebSocket message handling

### Integration Tests
- Create → join → vote → reveal → assign flow
- Multi-round continuation
- Session cleanup on end

### Manual Testing (QA)
- 5–10 concurrent participants, full flow
- Network disconnect → reconnect
- Multiple sessions simultaneously
- Edge case: session expires mid-voting

---

## Deployment

**Backend:**
- Deploy to Vercel free tier via `vercel.json`
- Environment: Node.js 18+
- Socket.io handling: Use Vercel Functions (serverless)

**Plugin:**
- Build existing webpack + new code
- Load in FigJam dev via manifest.json
- Connect plugin to backend via environment variable (session API URL)

**Rollout:**
- All work on DEV branch
- Master untouched until ready
- Release as v2 with changelog

---

## Success Criteria

✅ Users can create session + share link  
✅ 80+ participants join same session  
✅ Hidden vote → reveal → assign flow works  
✅ Final value written to FigJam sticky  
✅ Multi-round voting in one session  
✅ Vote history deleted after session  
✅ Real-time updates (< 500ms latency)  
✅ Session auto-expires after 1hr inactivity  
✅ Fallback to manual mode if backend down  

---

## Out of Scope (v2)

- User authentication / accounts
- Vote history persistence (deleted by design)
- Permanent session storage
- Mobile app
- Voting extensions (custom schemes beyond Fibonacci)
- Analytics / reporting

---

## Next Steps

1. Write implementation plan (writing-plans skill)
2. Set up backend structure
3. Implement WebSocket + session management
4. Build plugin UI tabs + modals
5. Integration testing
6. Deploy backend to Vercel
7. QA on real FigJam board
