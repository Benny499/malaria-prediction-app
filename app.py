from flask import Flask, render_template, request, jsonify, redirect
import pandas as pd
import pickle

app = Flask(__name__)

# Load model and feature columns
model = pickle.load(open('Gwatana_Benjamin_Jurima_malaria_classifier_model.pkl', 'rb'))
feature_columns = pickle.load(open('feature_columns.pkl', 'rb'))

# In-memory storage for last 5 predictions
recent_predictions = []

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract data
        name = request.form.get('name')
        age = int(request.form.get('age'))
        gender = request.form.get('gender')
        temperature = float(request.form.get('temperature'))

        # Initialize input dict
        input_data = {
            'age': age,
            'gender_male': 1 if gender == 'male' else 0,
            'gender_female': 1 if gender == 'female' else 0,
            'temperature': temperature
        }

        # Symptoms list
        symptoms = [
            'fever', 'headache', 'vomiting', 'diarrhoea', 'anaemia', 'cough',
            'convulsion', 'dizziness', 'loss_of_appetite', 'joint_pain',
            'chills', 'sweating', 'rapid_diagnostic_test_positive'
        ]

        # Add symptoms to input_data
        for symptom in symptoms:
            input_data[symptom] = int(request.form.get(symptom, 0))

        # Align with model features
        input_df = pd.DataFrame([input_data])
        input_df = input_df.reindex(columns=feature_columns, fill_value=0)

        # Predict
        prediction = model.predict(input_df)[0]

        if prediction == 1:
            result = "Malaria Detected"
            alert = "Malaria detected! Seek medical attention immediately."
        else:
            result = "No Malaria Detected"
            alert = "You appear to be malaria-free."

        # Store prediction
        recent_predictions.insert(0, {"name": name, "result": result, "alert": alert})
        if len(recent_predictions) > 5:
            recent_predictions.pop()

        return jsonify({
            "result": result,
            "alert": alert,
            "predictions": recent_predictions
        })

    except Exception as e:
        return jsonify({"result": "Error", "alert": str(e)})

@app.route('/reset')
def reset():
    recent_predictions.clear()
    return redirect('/')
