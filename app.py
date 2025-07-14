from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# Load trained model
model = pickle.load(open('Gwatana_Benjamin_Jurima_malaria_classifier_model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Collect form data
        age = int(request.form['age'])
        fever = int(request.form['fever'])
        headache = int(request.form['headache'])
        vomiting = int(request.form['vomiting'])
        rdt = int(request.form['rdt'])

        # Combine features for prediction (excluding parasite count & microscopy)
        features = np.array([[age, fever, headache, vomiting, rdt]])
        # Input features
        input_data = {
            'age': int(request.form['age']),
            'body_temperature': float(request.form['temperature']),
            'fever': int('fever' in request.form),
            'headache': int('headache' in request.form),
            'vomiting': int('vomiting' in request.form),
            'chills': int('chills' in request.form),
            'sweating': int('sweating' in request.form),
            'fatigue': int('fatigue' in request.form),
            'muscle_pain': int('muscle_pain' in request.form),
            'nausea': int('nausea' in request.form),
            'diarrhea': int('diarrhea' in request.form),
            'anemia': int('anemia' in request.form),
            'rapid_diagnostic_test': int('rdt' in request.form),
            'microscopy_result': int('microscopy' in request.form),
            'gender_Male': 1 if request.form['gender'] == 'Male' else 0
        }

        # Predict using model
        prediction = model.predict(features)[0]

        # Result message
        if prediction == 1:
            result = "Malaria Detected"
            alert = "⚠️ Medical attention is advised!"
        else:
            result = "No Malaria"
            alert = ""

        return render_template('index.html', result=result, alert=alert)

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
