from flask import Flask, jsonify, request
from scraper import get_jobs

app = Flask(__name__)

@app.route('/api/jobs', methods=['POST'])
def get_jobs_data():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400
    
    url = data.get("url")

    if not url:
        return jsonify({
            "error": "Missing 'url' parameter"
        }), 400

    maxItems = data.get("maxItems")

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