from flask import Flask, jsonify, request
from scraper import get_jobs
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route('/api/jobs', methods=['POST'])
def get_jobs_data():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    if not data or not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a non-empty JSON object"
        }), 400
    
    url = data.get("url")

    if not url:
        return jsonify({
            "error": "Missing 'url' parameter"
        }), 400

    maxItems = data.get("maxItems")

    if maxItems is not None: #si un user entre 0 en maxItems qui est consideré falsy , et if maxItems sera false, mais en realité la valeur est fournie.
        if not isinstance(maxItems, int) or isinstance(maxItems, bool) or maxItems <= 0:
            return jsonify({
            "error": "'maxItems' must be a positive integer"
        }), 400

    try:
        jobs = get_jobs(url, maxItems) if maxItems else get_jobs(url)

        return jsonify({
            "success": True,
            "count": len(jobs),
            "jobs": jobs
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)