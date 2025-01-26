from flask import Flask, request, render_template,redirect,session,url_for
import sqlite3
import google.generativeai as genai
import os
from dotenv import load_dotenv
import secrets


load_dotenv()

app = Flask(__name__)

#secret_key_setup
secret_key=secrets.token_hex(16)
app.config['SECRET_KEY']=secret_key

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Gemini API key is not set in the environment variables.")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

DATABASE = 'fertilizer.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soil TEXT,
            weather TEXT,
            fertilizer TEXT,
            amount REAL,
            crop TEXT,
            predicted_yield TEXT,
            description TEXT,
            raw_response TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def connect_db():
    return sqlite3.connect(DATABASE)

def store_prediction(soil, weather, fertilizer, amount, crop, predicted_yield, description, raw_response):
    with connect_db() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO predictions (soil, weather, fertilizer, amount, crop, predicted_yield, description, raw_response) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (soil, weather, fertilizer, amount, crop, predicted_yield, description, raw_response)
        )
        conn.commit()

def get_all_predictions():
    with connect_db() as conn:
        conn.row_factory = sqlite3.Row  
        c = conn.cursor()
        c.execute("SELECT * FROM predictions ORDER BY id DESC") 
        rows = c.fetchall()
    return [dict(row) for row in rows]


def predict_yield_with_gemini(soil, weather, fertilizer, amount, crop):
    prompt = (
        f"Given the following conditions for '{crop}' yield prediction:\n"
        f"- Soil: Type ={soil}, pH = 6.5, Nutrients = NPK (50-30-20), Organic matter = High, Texture = Loam, Depth = 1.2 meters, Drainage = Good\n"
        f"- {weather}: Temperature = 22°C, Rainfall = 500mm annually, Humidity = 80%, Sunlight hours = 8/day, Microclimate Variations: Temperature difference of 2°C across the field\n"
        f"- Fertilizer: Type = {fertilizer}, Application rate = {amount} kg/ha\n"
        "- Planting Date: Today\n"
        "- Planting Density: 55,000 plants/ha\n"
        "- Pest/Disease Pressure: Low\n"
        "- Weed Pressure: Moderate, Control: Herbicide application in early growth stage\n"
        "- Irrigation: Drip irrigation, Efficiency = 90%\n"
        "- Management Practices: Planting depth = 5 cm, Conventional cultivation and harvesting methods\n"
        "\n"
        "Based on the above conditions, please provide a yield prediction for {crop}. If precise prediction isn't possible, provide an estimated range, and mention any key factors that might impact yield."
    )

    try:
        response = model.generate_content(prompt)
        symbols_to_remove = '@#$%&*'
        print("Response from Gemini AI:", response)
        text_values = response.candidates[0].content.parts[0].text
        text_value=''.join([char for char in text_values if char not in symbols_to_remove])
        print("test",text_value)
    
        return {
            "yield": text_value,
            "description": "Prediction from Gemini AI",
            "raw_response": text_value
        }
        
    except Exception as e:
        print("Error during prediction:", str(e))
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/about')
def about():
    return render_template('about.html')    

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    try:
        soil = request.form.get('soil')
        weather = request.form.get('weather')
        fertilizer = request.form.get('fertilizer')
        amount = request.form.get('amount')
        crop = request.form.get('crop')

        if not all([soil, weather, fertilizer, amount, crop]):
            return render_template('index.html', error="All fields are required.")

        if not amount.replace('.', '', 1).isdigit():
            return render_template('index.html', error="Amount must be a valid number.")

        amount = float(amount)

        result = predict_yield_with_gemini(soil, weather, fertilizer, amount, crop)

        if result is None:
            return render_template('index.html', error="Error communicating with Gemini AI.")
        store_prediction(soil, weather, fertilizer, amount, crop, result["yield"], result["description"], result["raw_response"])

        session['result'] = result

        return render_template('index.html', result=result)    

    except Exception as e:
        return render_template('index.html', error=f"An unexpected error occurred: {str(e)}")

@app.route('/prediction')
def prediction():
    try:
        result = session.get('result', None)

        if not result:
            return redirect(url_for('index'))

        return render_template('prediction.html', result=result)

    except Exception as e:
        return render_template('prediction.html', error=f"An unexpected error occurred: {str(e)}")

@app.route('/all_responses')
def all_responses():
    predictions = get_all_predictions()
    return render_template('all_responses.html', predictions=predictions)

if __name__ == '__main__':
    app.run(debug=True)
