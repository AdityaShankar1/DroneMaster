# DroneMaster – Explainable Drone Mission Assignment System

## Overview
DroneMaster is an end-to-end decision system for assigning pilots and drones to enterprise missions under operational, regulatory, and priority constraints.

The system emphasizes:
- Explainability
- Auditability
- Priority-aware decision making
- Enterprise-readiness

Inspired by real-world drone operations at scale.

---

## Backend Capabilities (Python)

### Mission Assignment Engine
- Rule-based matching of pilots and drones
- Location, skills, certifications, capability checks
- Priority-aware scoring
- Strict vs soft constraint handling

### Explainability
- Every conflict includes human-readable reasons
- Violations are logged even for successful assignments

### Decision Logging
- Full audit trail per mission
- Timestamped decisions
- Approval-required flags
- Policy mode awareness

### Escalation Engine
- Automatically flags urgent unassigned missions
- Generates recommended human actions

### Google Sheets Integration
- Reads input data from Sheets
- Writes:
  - Assignments
  - Conflicts
  - Decision Log
  - Escalations
- Uses service account access

---

## Frontend (Next.js + TypeScript)

### Features
- Typed domain models
- Dashboard view
- Assignment visibility
- Conflict explainability
- Foundation for escalation UI

### Tech Stack
- Next.js (App Router)
- React
- TypeScript

---

## Why This Matters
This project models how real enterprise drone platforms:
- Balance automation with human oversight
- Provide explainable decisions
- Scale from rule engines to ML systems
- Maintain compliance and auditability

---

## Future Extensions
- Policy mode toggle (strict vs suggestive)
- Manual override UI
- ML-based scoring
- Simulation mode
- Realtime updates

---

## Status
Backend complete.  
Frontend MVP in progress.
