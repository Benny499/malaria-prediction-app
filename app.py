from flask import Flask, render_template, request, session, redirect, url_for
import pickle
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session storage

# Load model and feature columns
model = pickle.load(open('Gwatana_Benjamin_Jurima_malaria_classifier_model.pkl', 'rb'))
feature_columns = pickle.load(open('feature_columns.pkl', 'rb'))

@app.route('/')
def home():
    predictions = session.get('predictions', [])
    return render_template('form.html', predictions=predictions, result=None, alert=None, dark=False)

@app.route('/predict', methods=['POST'])
def predict():
    name = request.form.get('name', 'Anonymous')
    
    try:
        input_data = {col: int(request.form[col]) for col in feature_columns}
        df = pd.DataFrame([input_data])
        prediction = model.predict(df)[0]

        if prediction == 1:
            result = "Malaria Detected"
            alert = "⚠️ Medical attention is advised!"
        else:
            result = "No Malaria"
            alert = ""

        # Save last 5 predictions in session
        new_record = {
            "name": name,
            "result": result,
            "alert": alert
        }

        history = session.get('predictions', [])
        history.insert(0, new_record)
        session['predictions'] = history[:5]  # Keep only 5

        return render_template("form.html", result=result, alert=alert, predictions=session['predictions'], dark=False)

    except Exception as e:
        return f"Error: {e}"

@app.route('/reset')
def reset():
    session.pop('predictions', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
