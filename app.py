from flask import Flask, render_template, request
import joblib
import pandas as pd
from collections import deque

app = Flask(__name__)

# Load model and features
model = joblib.load("malaria_classifier_model.pkl")
features = joblib.load("feature_columns.pkl")

# Store last 5 predictions
last_predictions = deque(maxlen=5)

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
    result = None
    severity = None

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        parasite_count = int(request.form.get('parasite_count', 0))

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
            'parasite_count': parasite_count,
            'rapid_diagnostic_test': int('rdt' in request.form),
            'microscopy_result': int('microscopy' in request.form),
            'gender_Male': 1 if request.form['gender'] == 'Male' else 0
        }

        # Prepare for model
        input_df = pd.DataFrame([input_data])[features]
        prediction = model.predict(input_df)[0]
        result = "🦠 Malaria Detected" if prediction == 1 else "✅ No Malaria"

        # Classify severity
        if parasite_count > 0:
            severity = classify_severity(parasite_count)

        # Save to history
        last_predictions.appendleft({
            'name': name if name else None,
            'result': result,
            'severity': severity
        })

    return render_template('form.html', result=result, severity=severity, history=list(last_predictions))

if __name__ == '__main__':
    app.run(debug=True)
