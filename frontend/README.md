# RecroAI Frontend

A minimal dark-themed dashboard inspired by Notion for viewing and managing candidates.

## Features

- **Sidebar Navigation**: Browse jobs and switch between them
- **Candidate Table**: View all candidates with their scores
- **Score Bars**: Visual representation of candidate scores
- **Suspicious Flag Indicator**: Shows authenticity flags for candidates
- **Dark Theme**: Minimal, clean design inspired by Notion

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## API Integration

The app is configured to proxy API requests to `http://localhost:8000` (the FastAPI backend).

Update the API calls in `App.jsx` to connect to your backend:

```javascript
// Example API call
const response = await fetch('/api/scoring/score-all', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ job_id: 1 })
})
```

## Desktop Only

This dashboard is designed for desktop use only and is not optimized for mobile devices.
