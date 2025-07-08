from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)

# Load model and feature columns
model = joblib.load("malaria_classifier_model.pkl")
features = joblib.load("feature_columns.pkl")

@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Collect form input
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
            'parasite_count': int(request.form['parasite_count']),
            'rapid_diagnostic_test': int('rdt' in request.form),
            'microscopy_result': int('microscopy' in request.form),
            'gender_Male': 1 if request.form['gender'] == 'Male' else 0
        }

        # Create DataFrame and align columns
        input_df = pd.DataFrame([input_data])[features]

        # Predict
        prediction = model.predict(input_df)[0]
        result = "🦠 Malaria Detected" if prediction == 1 else "✅ No Malaria"

        return render_template('form.html', result=result)

    return render_template('form.html', result=None)

if __name__ == '__main__':
    app.run(debug=True)
