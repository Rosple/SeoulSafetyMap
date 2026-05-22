from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjMzMzljYTg2NzYzYjQ0ZTI4ZjQ4NjY2Mjc2YTMxYjU5IiwiaCI6Im11cm11cjY0In0="

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/route", methods=["POST"])
def route():
    data = request.json

    start = data["start"]
    end = data["end"]

    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [start["lng"], start["lat"]],
            [end["lng"], end["lat"]]
        ],
        "alternative_routes": {
            "target_count": 3,
            "weight_factor": 1.6,
            "share_factor": 0.6
        }
    }

    response = requests.post(url, json=body, headers=headers)
    result = response.json()

    if response.status_code != 200:
        return jsonify({
            "error": True,
            "message": result
        }), 400

    routes = []

    for feature in result["features"]:
        routes.append({
            "coordinates": feature["geometry"]["coordinates"],
            "distance": feature["properties"]["summary"]["distance"],
            "duration": feature["properties"]["summary"]["duration"]
        })

    return jsonify({
        "routes": routes
    })

if __name__ == "__main__":
    app.run(debug=True)
