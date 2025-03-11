# RegRely

AI-powered regulatory compliance dashboard for financial institutions. Stay informed with the latest regulatory updates and banking compliance news, powered by advanced AI analysis.

## Features

- Real-time regulatory updates from federal and state regulators
- Institution-specific regulatory landscape analysis
- Customized updates based on your institution's regulators
- Intelligent caching system to optimize API usage
- Beautiful, responsive web interface

## Setup

1. Clone the repository:
```bash
git clone https://github.com/tjagdish/RegRely.git
cd RegRely
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
export PERPLEXITY_API_KEY='your_api_key_here'
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5001`

## API Endpoints

- `GET /`: Landing page
- `GET /landscape-analyst`: Regulatory landscape analysis dashboard
- `POST /api/institution/regulators`: Get regulators for a specific institution
- `GET /api/updates/<period>`: Get regulatory updates (period: daily, weekly, monthly)

## Technologies Used

- Python/Flask for the backend
- HTML/CSS/JavaScript for the frontend
- Perplexity API for AI-powered analysis
- Flask-CORS for cross-origin resource sharing
- Gunicorn for production deployment 