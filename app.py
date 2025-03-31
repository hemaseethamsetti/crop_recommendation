import os
import pickle
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__, template_folder="templates")
print("Current Working Directory:", os.getcwd())

# Load models
crop_model = pickle.load(open(r"C:\Users\hemas\Desktop\crop_re\backend\crop_recommendation (2).pkl", "rb"))
yield_model = pickle.load(open(r"C:\Users\hemas\Desktop\crop_re\backend\yield_prediction (1).pkl", "rb"))

# Load dataset
try:
    dataset = pd.read_csv(r"C:\Users\hemas\Desktop\crop_re\backend\upload.csv")
    print("Dataset loaded successfully:", dataset.head())  # Debugging line
except Exception as e:
    print(f"Error loading dataset: {str(e)}")
    dataset = None  # Explicitly set to None for debugging

if 'dataset' not in globals() or dataset is None:
    raise ValueError("Dataset is not loaded correctly.")


print("Dataset Columns:", dataset.columns)
print("Dataset Sample:", dataset.head())

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
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

# Load encoders
state_encoder = pickle.load(open(r"C:\Users\hemas\Desktop\crop_re\backend\state_encoder.pkl", "rb"))
soil_type_encoder = pickle.load(open(r"C:\Users\hemas\Desktop\crop_re\backend\soil_type_encoder.pkl", "rb"))
season_encoder = pickle.load(open(r"C:\Users\hemas\Desktop\crop_re\backend\season_encoder.pkl", "rb"))

@app.route('/predict_crop', methods=['POST'])
def predict_crop():
    try:
        data = request.get_json()
        state = data['state']
        soil_type = data['soil_type']
        season = data['season']

        # Clean input values
        state_cleaned = state.strip().lower()
        soil_type_cleaned = soil_type.strip()
        season_cleaned = season.strip()

        required_columns = {'State_Name', 'soil_type', 'Season', 'Crop'}
        if not required_columns.issubset(dataset.columns):
            return jsonify({'error': 'Dataset is missing required columns'}), 500

        dataset['State_Name'] = dataset['State_Name'].astype(str).str.lower()
        dataset['soil_type'] = dataset['soil_type'].astype(str).str.strip()
        dataset['Season'] = dataset['Season'].astype(str).str.strip()

        filtered_data = dataset[
            (dataset['State_Name'] == state_cleaned) &
            (dataset['soil_type'] == soil_type_cleaned) &
            (dataset['Season'] == season_cleaned)
        ]

        if filtered_data.empty:
            return jsonify({'error': 'No matching data found for the given inputs'}), 400

        recommended_crop = filtered_data['Crop'].iloc[0]
        return jsonify({'recommended_crop': recommended_crop})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/crop_yield')
def crop_yield_page():
    return render_template("crop_yield.html")

import random

@app.route('/predict_yield', methods=['POST'])
def predict_yield():
    try:
        data = request.get_json()
        print("Received Data:", data)  # Debugging line

        state = data['state']
        soil_type = data['soil_type']
        area = float(data['area'])
        crop = data['crop']

        # Random yield generation based on crop type (in tons)
        crop_yield_ranges = {
            'Arecanut': (2, 4),
            'Banana': (15, 25),
            'Dry chillies': (0.5, 1.5),
            'Coconut': (3, 5),
            'Cotton(lint)': (1.5, 3),
            'Dry ginger': (1, 2),
            'Groundnut': (1, 2.5)
        }

        if crop not in crop_yield_ranges:
            return jsonify({'error': 'Crop not recognized for yield prediction.'}), 400

        min_yield, max_yield = crop_yield_ranges[crop]
        predicted_yield = random.uniform(min_yield, max_yield) * (area / 10000)  # Adjusting for area in hectares

        return jsonify({'predicted_yield': round(predicted_yield, 2)})

    except Exception as e:
        print("Error:", str(e))  # Debugging line
        return jsonify({'error': str(e)}), 500

   

@app.route('/weather')
def weather():
    return render_template("weather.html")

#  Crop Recommendation Options (Soil Types & Seasons)
@app.route('/get_recommendation_options', methods=['GET'])
def get_recommendation_options():
    state = request.args.get('state', '').strip().lower()

    if not state:
        return jsonify({'error': 'State parameter is missing'}), 400

    state_data = dataset[dataset['State_Name'].str.lower() == state]

    if state_data.empty:
        return jsonify({'soil_types': [], 'seasons': [], 'message': 'No data found for the selected state'})

    soil_types = state_data['soil_type'].dropna().unique().tolist()
    seasons = state_data['Season'].dropna().unique().tolist()

    return jsonify({
        'soil_types': soil_types,
        'seasons': seasons
    })

#  Crop Yield Options (Soil Types & Crops)
@app.route('/get_yield_options', methods=['GET'])
def get_yield_options():
    state = request.args.get('state', '').strip().lower()

    if not state:
        return jsonify({'error': 'State parameter is missing'}), 400

    state_data = dataset[dataset['State_Name'].str.lower() == state]

    if state_data.empty:
        return jsonify({'soil_types': [], 'crops': [], 'message': 'No data found for the selected state'})

    soil_types = state_data['soil_type'].dropna().unique().tolist()
    crops = state_data['Crop'].dropna().unique().tolist()

    return jsonify({'soil_types': soil_types, 'crops': crops})

if __name__ == "__main__":
    app.run(debug=True)
