from flask import Flask, request, render_template
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# NASA API configuration
NASA_API_KEY = "zIH7mNuXTgXz5Mw771KyjvlbHprVnQ3GWF9TZpQ9"  # Replace with your actual NASA API key
BASE_URL_FLARES = "https://api.nasa.gov/DONKI/FLR"
BASE_URL_CME = "https://api.nasa.gov/DONKI/CME"
BASE_URL_ASTEROIDS = "https://api.nasa.gov/neo/rest/v1/feed"

# Fetch recent solar flare data
def get_recent_solar_flare(start_date, end_date):
    params = {"startDate": start_date, "endDate": end_date, "api_key": NASA_API_KEY}
    response = requests.get(BASE_URL_FLARES, params=params)
    if response.status_code == 200:
        flares = response.json()
        if flares:
            # Extract relevant data from each solar flare entry
            flare_list = []
            for flare in flares:
                flare_data = {
                    "startTime": flare.get("beginTime"),
                    "peakTime": flare.get("peakTime"),
                    "endTime": flare.get("endTime"),
                    "classType": flare.get("classType", "N/A"),
                    "sourceLocation": flare.get("sourceLocation", "Unknown location")
                }
                flare_list.append(flare_data)
            return flare_list
    return []


# Fetch recent CME data
def get_recent_cme(start_date, end_date):
    params = {"startDate": start_date, "endDate": end_date, "api_key": NASA_API_KEY}
    response = requests.get(BASE_URL_CME, params=params)
    if response.status_code == 200:
        cmes = response.json()
        if cmes:
            # Extract relevant data from each CME entry
            cme_list = []
            for cme in cmes:
                cme_data = {
                    "startTime": cme.get("startTime"),
                    "sourceLocation": cme.get("sourceLocation", "Unknown location")
                }
                cme_list.append(cme_data)
            return cme_list
    return []



# Fetch recent asteroid close-approach data
def get_recent_asteroid(start_date, end_date):
    params = {"start_date": start_date, "end_date": end_date, "api_key": NASA_API_KEY}
    response = requests.get(BASE_URL_ASTEROIDS, params=params)
    if response.status_code == 200:
        data = response.json()
        asteroids = data.get("near_earth_objects", {})
        
        # Flatten the list of asteroids into a single list and sort by close approach date
        all_asteroids = []
        for date in asteroids:
            for asteroid in asteroids[date]:
                close_approach_data = asteroid.get("close_approach_data", [])
                if close_approach_data:
                    approach = close_approach_data[0]  # Take the first close approach data
                    asteroid_data = {
                        "name": asteroid.get("name", "Unknown"),
                        "close_approach_date": approach.get("close_approach_date"),
                        "miss_distance_km": approach.get("miss_distance", {}).get("kilometers", "N/A"),
                        "relative_velocity_km_s": approach.get("relative_velocity", {}).get("kilometers_per_second", "N/A"),
                        "diameter_min_km": asteroid.get("estimated_diameter", {}).get("kilometers", {}).get("estimated_diameter_min", "N/A"),
                        "diameter_max_km": asteroid.get("estimated_diameter", {}).get("kilometers", {}).get("estimated_diameter_max", "N/A"),
                        "is_potentially_hazardous": asteroid.get("is_potentially_hazardous_asteroid", False)
                    }
                    all_asteroids.append(asteroid_data)
        
        # Sort by the closest approach date for better organization
        all_asteroids.sort(key=lambda x: x['close_approach_date'])
        return all_asteroids
    return []


@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/cme', methods=["GET", "POST"])
def cme_page():
    # Set default date range (last 7 days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    if request.method == "POST":
        start_date = request.form.get("start_date", start_date)
        end_date = request.form.get("end_date", end_date)

    cme = get_recent_cme(start_date, end_date)
    return render_template('cme.html', cme=cme, start_date=start_date, end_date=end_date)

@app.route('/solarflair', methods=["GET", "POST"])
def solar_flare_page():
    # Set default date range (last 7 days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    if request.method == "POST":
        start_date = request.form.get("start_date", start_date)
        end_date = request.form.get("end_date", end_date)

    solar_flare = get_recent_solar_flare(start_date, end_date)
    return render_template('solarflair.html', solar_flare=solar_flare, start_date=start_date, end_date=end_date)

@app.route('/asteroids', methods=["GET", "POST"])
def asteroid_page():
    # Set default date range (last 7 days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    if request.method == "POST":
        start_date = request.form.get("start_date", start_date)
        end_date = request.form.get("end_date", end_date)

    asteroids = get_recent_asteroid(start_date, end_date)
    return render_template('asteroids.html', asteroids=asteroids, start_date=start_date, end_date=end_date)


if __name__ == '__main__':
    app.run(debug=True)
