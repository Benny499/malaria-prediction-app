import os
import pickle
from math import isfinite

import pandas as pd
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from extensions import db, limiter
from models import Prediction

prediction = Blueprint('prediction', __name__)

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, 'Gwatana_Benjamin_Jurima_malaria_classifier_model.pkl')
FEATURES_PATH = os.path.join(BASE_DIR, 'feature_columns.pkl')

with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

with open(FEATURES_PATH, 'rb') as f:
    feature_columns = pickle.load(f)


def serialize_prediction(item):
    return {
        'id': item.id,
        'name': item.patient_name or '',
        'result': item.result,
        'confidence': item.confidence,
        'timestamp': item.timestamp.isoformat()
    }


@prediction.route('/history', methods=['GET'])
@login_required
def history():
    items = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.timestamp.desc()).limit(50).all()
    return jsonify({'predictions': [serialize_prediction(item) for item in items]})


@prediction.route('/history/<int:prediction_id>', methods=['DELETE'])
@login_required
@limiter.limit('30 per minute')
def delete_prediction(prediction_id):
    item = Prediction.query.filter_by(id=prediction_id, user_id=current_user.id).first()
    if item is None:
        return jsonify({'error': 'Prediction not found.'}), 404

    db.session.delete(item)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'The prediction could not be deleted.'}), 500

    return jsonify({'status': 'deleted', 'id': prediction_id})


@prediction.route('/history', methods=['DELETE'])
@login_required
@limiter.limit('5 per minute')
def delete_history():
    Prediction.query.filter_by(user_id=current_user.id).delete()
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'Prediction history could not be cleared.'}), 500

    return jsonify({'status': 'cleared'})


@prediction.route('/predict', methods=['POST'])
@login_required
@limiter.limit('30 per minute')
def predict():
    data = request.form
    name = data.get('name', '').strip()
    gender_raw = data.get('gender', '').strip().lower()
    temp_unit = data.get('temp_unit', 'C').strip().upper()

    if not name or len(name) > 100:
        return jsonify({'error': 'Patient name is required and must be 100 characters or fewer.'}), 400

    if gender_raw not in {'male', 'female'}:
        return jsonify({'error': 'Gender must be male or female.'}), 400

    if temp_unit not in {'C', 'F'}:
        return jsonify({'error': 'Temperature unit must be C or F.'}), 400

    try:
        age = float(data.get('age', ''))
        temperature = float(data.get('temperature', ''))
    except (TypeError, ValueError):
        return jsonify({'error': 'Age and temperature must be valid numbers.'}), 400

    if not isfinite(age) or age < 0 or age > 120:
        return jsonify({'error': 'Age must be between 0 and 120.'}), 400

    if temp_unit == 'F':
        temperature = (temperature - 32) * 5.0 / 9.0

    if not isfinite(temperature) or temperature < 25 or temperature > 43:
        return jsonify({'error': 'Temperature must be between 25°C and 43°C.'}), 400

    gender = 0 if gender_raw == 'male' else 1

    def s(key):
        return 1 if data.get(key) == '1' else 0

    input_dict = {
        'age': age,
        'temperature': temperature,
        'gender': gender,
        'fever': s('fever'),
        'headache': s('headache'),
        'vomiting': s('vomiting'),
        'diarrhoea': s('diarrhoea'),
        'anaemia': s('anaemia'),
        'cough': s('cough'),
        'convulsion': s('convulsion'),
        'dizziness': s('dizziness'),
        'loss_of_appetite': s('loss_of_appetite'),
        'joint_pain': s('joint_pain'),
        'chills': s('chills'),
        'sweating': s('sweating'),
        'rapid_diagnostic_test_positive': s('rapid_diagnostic_test_positive'),
    }

    input_df = pd.DataFrame([input_dict])[feature_columns]

    try:
        pred_result = model.predict(input_df)[0]
        confidence = float(model.predict_proba(input_df)[0].max())
    except (ValueError, TypeError):
        return jsonify({'error': 'The prediction model could not process this input.'}), 500

    result_label = 'Malaria Detected' if pred_result == 1 else 'No Malaria Detected'
    alert_text = 'Malaria detected. Please seek medical attention immediately.' \
        if pred_result == 1 else 'No malaria detected. Stay healthy!'

    record = Prediction(
        result=result_label,
        confidence=confidence,
        user_id=current_user.id,
        patient_name=name
    )
    try:
        db.session.add(record)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': 'The prediction was not saved. Please try again.'}), 500

    history = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.timestamp.desc()).limit(50).all()

    predictions_list = [serialize_prediction(item) for item in history]

    return jsonify({
        'name': name,
        'result': result_label,
        'alert': alert_text,
        'confidence': round(confidence, 4),
        'predictions': predictions_list
    })


@prediction.route('/reset', methods=['GET'])
@login_required
def reset():
    return jsonify({'status': 'ok'})