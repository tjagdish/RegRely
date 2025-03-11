# RegRely - Regulatory Updates Dashboard

This application provides real-time regulatory updates for the financial sector using the Perplexity Sonar API.

## Features

- Live regulatory updates from the past 24 hours, week, and month
- Caching mechanism to reduce API calls
- Beautiful, responsive UI
- Automatic refresh functionality

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. The Perplexity API key is already configured in the application.

3. Run the Flask server:
```bash
python app.py
```

4. Open `landscape-analyst.html` in your web browser.

## How It Works

- The application uses Flask as a backend server to handle API requests and caching
- Regulatory updates are fetched from Perplexity Sonar API and cached for 24 hours
- The frontend makes API calls to the Flask backend instead of directly to Perplexity
- Updates are displayed in a responsive card layout with importance indicators

## Cache Mechanism

- Updates are cached for 24 hours to minimize API usage
- Separate caches are maintained for daily, weekly, and monthly updates
- Cache is automatically refreshed when it expires

## API Endpoints

- GET `/api/updates/daily` - Get updates from the past 24 hours
- GET `/api/updates/weekly` - Get updates from the past week
- GET `/api/updates/monthly` - Get updates from the past month 