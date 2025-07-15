from flask import Flask, render_template, request, jsonify, redirect
import pandas as pd
import pickle

app = Flask(__name__)

# Load your model and feature columns
model = pickle.load(open('Gwatana_Benjamin_Jurima_malaria_classifier_model.pkl', 'rb'))
with open('feature_columns.pkl', 'rb') as f:
    feature_columns = pickle.load(f)

last_predictions = []

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/predict', methods=['POST'])
def predict():
    form = request.form.to_dict()
    name = form.pop('name', 'Anonymous')
    age = int(form.get('age', 0))
    gender = form.get('gender', '')
    temperature = float(form.get('temperature', 0))

    features = {col: 0 for col in feature_columns}
    features.update({
        'age': age,
        'gender_male': 1 if gender == 'male' else 0,
        'gender_female': 1 if gender == 'female' else 0,
        'temperature': temperature
    })

    for key in form:
        if key in features:
            features[key] = int(form[key])

    input_df = pd.DataFrame([features])
    prediction = model.predict(input_df)[0]
    result = 'Malaria Detected' if prediction == 1 else 'No Malaria Detected'
    alert = '⚠️ Malaria has been detected!' if prediction == 1 else '✅ Patient is malaria-free.'

    # Store last 5 predictions
    last_predictions.insert(0, {'name': name, 'result': result, 'alert': alert})
    if len(last_predictions) > 5:
        last_predictions.pop()

    return jsonify({
        'result': result,
        'alert': alert,
        'predictions': last_predictions
    })

@app.route('/reset')
def reset():
    last_predictions.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
