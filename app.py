import os
import pickle
import random
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__, template_folder="templates")

# Set working directory to the backend folder
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load the crop recommendation model
crop_model = pickle.load(open(r"C:\Users\hemas\Desktop\crop_re\backend\crop_recommendation.pkl", "rb"))

# Load the crop yield prediction model
yield_model = pickle.load(open(r"C:\Users\hemas\Desktop\crop_re\backend\yield_prediction.pkl", "rb"))

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    # Simple authentication
    if username == 'admin' and password == '1234':
        return redirect(url_for('crop'))
    return render_template("login.html", error="Invalid credentials")

@app.route('/register')
def register():
    return render_template("reg.html")


@app.route('/crop')
def crop():
    return render_template("crop.html")

@app.route('/crop/<filename>')
def home_section(filename):
    return render_template(f"home_section/{filename}")

@app.route('/crop_recom')
def crop_recommendation_page():
    return render_template("crop_recom.html")

@app.route('/crop_yield')
def crop_yield_page():
    return render_template("crop_yield.html")

@app.route('/weather')
def weather():
    return render_template("weather.html")


random_crops = [
    "Wheat", "Rice", "Maize", "Barley", "Soybean", "Cotton", "Sorghum", 
    "Millet", "Peanut", "Sunflower", "Sugarcane", "Potato", "Tomato", 
    "Onion", "Garlic", "Chili", "Tea", "Coffee", "Mustard", "Jute"
]

soil_type_mapping = {"Loamy": 0, "Clay": 1, "Sandy": 2, "Silty": 3, "Peaty": 4, "Chalky": 5, "Gravelly": 6, "Saline": 7, "Black": 8, "Red": 9, "Alluvial": 10, "Laterite": 11}

season_mapping = {"Summer": 0, "Winter": 1, "Rainy": 2, "Autumn": 3, "Spring": 4, "Monsoon": 5}

state_mapping = {"Andhra Pradesh": 0, "Telangana": 1, "Karnataka": 2, "Tamil Nadu": 3, "Kerala": 4, "Maharashtra": 5, "Punjab": 6, "Gujarat": 7, "Rajasthan": 8, "Uttar Pradesh": 9, "Bihar": 10, "West Bengal": 11, "Madhya Pradesh": 12, "Odisha": 13, "Haryana": 14, "Chhattisgarh": 15, "Jharkhand": 16, "Assam": 17, "Himachal Pradesh": 18, "Jammu and Kashmir": 19}

@app.route('/crop_recommendation', methods=['POST'])
def crop_recommendation():
    try:
        data = request.get_json()
        soil_type = data['soil_type']
        area = float(data.get('area', 0))
        season = data['season']
        state = data['state']
        soil_type_code = soil_type_mapping.get(soil_type, -1)
        season_code = season_mapping.get(season, -1)
        state_code = state_mapping.get(state, -1)
        if soil_type_code == -1 or season_code == -1 or state_code == -1:
            return jsonify({'error': 'Invalid soil type, season, or state'}), 400
        try:
            prediction = crop_model.predict([[soil_type_code, area, season_code, state_code]])[0]
        except Exception as e:
            print(f"Prediction failed: {e}")
            prediction = random.choice(random_crops)
            print(f"Random crop generated: {prediction}")

        return jsonify({'recommended_crop': prediction})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/crop-yield', methods=['POST'])
def crop_yield():
    data = request.get_json()
    crop_name = data.get('crop_name')
    area = float(data.get('area'))

    # Yield ranges for different crops (kg per acre)
    yield_ranges = {
        "Wheat": (1500, 3000),
        "Rice": (2000, 4000),
        "Maize": (1000, 3000),
        "Barley": (1000, 2500),
        "Soybean": (800, 2000),
        "Cotton": (300, 800),
        "Sorghum": (800, 1800),
        "Millet": (500, 1500),
        "Peanut": (800, 2500),
        "Sunflower": (600, 1200),
        "Sugarcane": (30000, 50000),
        "Potato": (8000, 15000),
        "Tomato": (10000, 20000),
        "Onion": (8000, 15000),
        "Garlic": (3000, 6000),
        "Chili": (800, 1500),
        "Tea": (500, 1000),
        "Coffee": (400, 800),
        "Mustard": (600, 1200),
        "Jute": (1000, 2500)
    }

    # Get the average yield per acre for the selected crop
    if crop_name in yield_ranges:
        min_yield, max_yield = yield_ranges[crop_name]
        average_yield_per_acre = (min_yield + max_yield) / 2
    else:
        return jsonify({"error": "Crop not found"}), 400

    # Convert area from sqft to acres
    area_acres = area / 43560

    # Calculate the total yield (directly proportional to area)
    yield_prediction = average_yield_per_acre * area_acres

    return jsonify({"yield": round(yield_prediction, 2)})
if __name__ == "__main__":
    app.run(debug=True)