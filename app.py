from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import pickle

app = Flask(__name__)

# Load model and features
model = pickle.load(open('Gwatana_Benjamin_Jurima_malaria_classifier_model.pkl', 'rb'))
feature_columns = pickle.load(open('feature_columns.pkl', 'rb'))  # Should contain ['age', 'fever', 'headache', 'vomiting', 'rdt']

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Build input dictionary based on feature columns
        input_data = {}
        for col in feature_columns:
            input_data[col] = int(request.form[col])

        input_df = pd.DataFrame([input_data])

        # Predict
        prediction = model.predict(input_df)[0]

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
