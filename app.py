from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)

# Load model and feature columns
model = joblib.load("malaria_classifier_model.pkl")
features = joblib.load("feature_columns.pkl")

# Severity classifier
def classify_severity(parasite_count):
    if parasite_count < 1000:
        return "Mild"
    elif 1000 <= parasite_count <= 9999:
        return "Mild to Moderate"
    elif 10000 <= parasite_count <= 99999:
        return "Moderate"
    elif 100000 <= parasite_count <= 249999:
        return "Severe"
    else:
        return "Very Severe / Critical"

@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Get diagnosis method and parasite count for severity
        diagnosis_method = request.form.get('diagnosis_method')
        parasite_count = request.form.get('parasite_count')

        severity = None
        if diagnosis_method == "Microscopy" and parasite_count:
            try:
                parasite_count = int(parasite_count)
                severity = classify_severity(parasite_count)
            except:
                severity = "Invalid input"

        # Collect model input
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
            'parasite_count': int(request.form['parasite_count']) if 'parasite_count' in request.form and request.form['parasite_count'] else 0,
            'rapid_diagnostic_test': int('rdt' in request.form),
            'microscopy_result': int('microscopy' in request.form),
            'gender_Male': 1 if request.form['gender'] == 'Male' else 0
        }

        # Create DataFrame and align with model
        input_df = pd.DataFrame([input_data])[features]
        prediction = model.predict(input_df)[0]
        result = "🦠 Malaria Detected" if prediction == 1 else "✅ No Malaria"

        return render_template('form.html', result=result, severity=severity)

    return render_template('form.html', result=None, severity=None)

if __name__ == '__main__':
    app.run(debug=True)
