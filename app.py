from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjMzMzljYTg2NzYzYjQ0ZTI4ZjQ4NjY2Mjc2YTMxYjU5IiwiaCI6Im11cm11cjY0In0="

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/geocode", methods=["POST"])
def geocode():
    data = request.json
    text = data["text"]

    url = "https://api.openrouteservice.org/geocode/search"

    params = {
        "api_key": ORS_API_KEY,
        "text": text,
        "boundary.country": "KR",
        "size": 1
    }

    response = requests.get(url, params=params)
    result = response.json()

    if response.status_code != 200 or len(result.get("features", [])) == 0:
        return jsonify({"error": True, "message": "주소를 찾지 못했습니다."}), 400

    feature = result["features"][0]
    lng, lat = feature["geometry"]["coordinates"]

    return jsonify({
        "lat": lat,
        "lng": lng,
        "label": feature["properties"].get("label", text)
    })

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
        return jsonify({"error": True, "message": result}), 400

    routes = []

    for feature in result["features"]:
        routes.append({
            "coordinates": feature["geometry"]["coordinates"],
            "distance": feature["properties"]["summary"]["distance"],
            "duration": feature["properties"]["summary"]["duration"]
        })

    return jsonify({"routes": routes})

if __name__ == "__main__":
    app.run(debug=True)
