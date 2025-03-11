from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__, static_url_path='')

# Configure CORS with more permissive settings
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 120  # Cache preflight requests for 2 minutes
    }
})

# Cache storage
cache = {
    'daily': {'data': None, 'timestamp': None},
    'weekly': {'data': None, 'timestamp': None},
    'monthly': {'data': None, 'timestamp': None},
    'institutions': {}  # Cache for institution-specific data
}

PERPLEXITY_API_KEY = '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'
API_ENDPOINT = 'https://api.perplexity.ai/chat/completions'

@app.route('/')
def serve_landing():
    """Serve the landing page"""
    return send_from_directory('.', 'landing-page.html')

@app.route('/landscape-analyst')
def serve_landscape_analyst():
    """Serve the landscape analyst page"""
    return send_from_directory('.', 'landscape-analyst.html')

def get_institution_regulators(institution_name):
    """Query Perplexity API to get regulators for a specific institution"""
    prompt = f"""Return ONLY a JSON object (no other text) containing the federal and state regulators responsible for {institution_name}.
The response should follow this EXACT format:
{{
    "federal_regulators": [
        {{
            "name": "Regulator name",
            "responsibilities": "What this regulator oversees for the institution"
        }}
    ],
    "state_regulators": [
        {{
            "name": "Regulator name",
            "state": "State name",
            "responsibilities": "What this regulator oversees for the institution"
        }}
    ]
}}

IMPORTANT: Return ONLY the JSON object. Do not include any other text.""".strip()

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a JSON-only response bot specializing in financial regulation. You must respond with valid JSON only, no other text."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        if result.get("choices") and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            try:
                # Clean the content - remove any text before { and after }
                content = content[content.find("{"):content.rfind("}")+1]
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON from API response: {content}")
                print(f"Error: {e}")
                return None
        return None
    except Exception as e:
        print(f"Error querying Perplexity API: {e}")
        return None

def get_regulatory_updates(time_period, regulators=None):
    """
    Query Perplexity API for regulatory updates based on time period and optional regulators list
    """
    time_map = {
        'daily': 'past 24 hours',
        'weekly': 'past week',
        'monthly': 'past month'
    }
    
    regulator_filter = ""
    if regulators:
        regulator_names = [reg["name"] for reg in regulators.get("federal_regulators", [])]
        regulator_names.extend([reg["name"] for reg in regulators.get("state_regulators", [])])
        regulator_filter = f" specifically from these regulators: {', '.join(regulator_names)}"
    
    prompt = f"""Return ONLY a JSON array (no other text) containing the latest banking and financial regulatory updates from the {time_map[time_period]}{regulator_filter}.
Each object in the array must follow this EXACT format (up to 4 objects total):
{{
    "source_name": "Name of regulatory body (e.g., Federal Reserve, SEC, OCC)",
    "source_date": "Today, HH:MM AM/PM" or "MM/DD/YYYY, HH:MM AM/PM",
    "title": "Title of the regulatory update",
    "summary": "A 2-3 sentence summary of the update",
    "importance": "critical" or "important" or "info",
    "citations": ["URL1", "URL2"]
}}

IMPORTANT: Return ONLY the JSON array. Do not include any other text before or after the array.""".strip()

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a JSON-only response bot. You must respond with valid JSON only, no other text."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        if result.get("choices") and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            try:
                content = content[content.find("["):content.rfind("]")+1]
                parsed_content = json.loads(content)
                if not isinstance(parsed_content, list):
                    print("API returned non-array response:", content)
                    return []
                return parsed_content
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON from API response: {content}")
                print(f"Error: {e}")
                return []
        return []
    except Exception as e:
        print(f"Error querying Perplexity API: {e}")
        return []

def should_refresh_cache(timestamp):
    """Check if cache needs to be refreshed"""
    if timestamp is None:
        return True
    return datetime.now() - timestamp > timedelta(hours=24)

@app.route('/api/institution/regulators', methods=['POST'])
def get_regulators():
    """Get regulators for a specific institution"""
    try:
        data = request.get_json()
        if not data:
            print("Error: No JSON data received")
            return jsonify({'error': 'No data received. Please ensure you\'re sending JSON data.'}), 400
            
        institution_name = data.get('institution')
        if not institution_name:
            print("Error: No institution name provided")
            return jsonify({'error': 'Institution name is required'}), 400
            
        # Log request details
        print(f"Processing request for institution: {institution_name}")
        print(f"Request headers: {dict(request.headers)}")
            
        # Check cache
        if institution_name in cache['institutions']:
            inst_cache = cache['institutions'][institution_name]
            if not should_refresh_cache(inst_cache.get('timestamp')):
                print(f"Returning cached data for {institution_name}")
                return jsonify(inst_cache['regulators'])
        
        # Query API and update cache
        print(f"Querying Perplexity API for {institution_name}")
        regulators = get_institution_regulators(institution_name)
        if regulators is None:
            print(f"Failed to get regulators from API for {institution_name}")
            return jsonify({'error': 'Failed to get regulators. API request failed.'}), 500
            
        # Initialize or update institution cache
        cache['institutions'][institution_name] = {
            'regulators': regulators,
            'timestamp': datetime.now(),
            'updates': {
                'daily': {'data': None, 'timestamp': None},
                'weekly': {'data': None, 'timestamp': None},
                'monthly': {'data': None, 'timestamp': None}
            }
        }
        
        print(f"Successfully processed request for {institution_name}")
        return jsonify(regulators)
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your request.',
            'details': str(e)
        }), 500

@app.route('/api/updates/<period>')
def get_updates(period):
    if period not in ['daily', 'weekly', 'monthly']:
        return jsonify({'error': 'Invalid period'}), 400
        
    institution_name = request.args.get('institution')
    
    if not institution_name:
        # Handle non-institution specific updates (original behavior)
        if cache[period]['data'] is not None and not should_refresh_cache(cache[period]['timestamp']):
            return jsonify(cache[period]['data'])
            
        updates = get_regulatory_updates(period)
        cache[period]['data'] = updates
        cache[period]['timestamp'] = datetime.now()
        return jsonify(updates)
    
    # Handle institution-specific updates
    if institution_name not in cache['institutions']:
        return jsonify({'error': 'Institution not found. Please submit institution details first.'}), 404
        
    inst_cache = cache['institutions'][institution_name]
    period_cache = inst_cache['updates'][period]
    
    if period_cache['data'] is not None and not should_refresh_cache(period_cache['timestamp']):
        return jsonify(period_cache['data'])
        
    updates = get_regulatory_updates(period, inst_cache['regulators'])
    period_cache['data'] = updates
    period_cache['timestamp'] = datetime.now()
    
    return jsonify(updates)

if __name__ == '__main__':
    # Development
    app.run(debug=True, port=5001)
else:
    # Production
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production' 