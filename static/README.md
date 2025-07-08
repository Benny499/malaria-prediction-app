# 🦠 Malaria Diagnosis Prediction App

This project uses machine learning to predict whether a patient is likely to be infected with **malaria** based on clinical symptoms, body measurements, and test results. It includes a trained classification model and a responsive web app built with **Flask**.

---

## 📌 Project Overview

- 📊 **Goal**: Predict malaria presence from clinical inputs
- 🤖 **Model Used**: Logistic Regression
- 💻 **App Type**: Flask Web Application
- 🧠 **Accuracy**: 99.8% (based on test data)
- 💾 **Data Type**: CSV dataset with symptoms and lab features

---

## 🧪 Features in the Dataset

| Feature                 | Description                            |
|-------------------------|----------------------------------------|
| `age`                   | Patient's age in years                 |
| `gender`                | Male or Female                         |
| `body_temperature`      | Measured in Celsius                    |
| `fever`                | Fever presence (1/0)                   |
| `headache`             | Headache presence                      |
| `vomiting`             | Vomiting symptom                       |
| `chills`               | Chills or shivering                    |
| `sweating`             | Excessive sweating                     |
| `fatigue`              | Feeling of tiredness                   |
| `muscle_pain`          | Muscle pain                            |
| `nausea`, `diarrhea`   | Gastro symptoms                        |
| `anemia`               | Anemia detection                       |
| `parasite_count`       | Parasites per microliter of blood      |
| `rapid_diagnostic_test`| Result of RDT (0/1)                    |
| `microscopy_result`    | Result from microscope (0/1)           |
| `malaria_test_result`  | **Target variable**: 0 = No Malaria, 1 = Malaria

---

## 🧠 Model Performance

| Metric        | Score     |
|---------------|-----------|
| Accuracy      | **100%**  |
| Precision     | 1.00      |
| Recall        | 1.00      |
| F1-Score      | 1.00      |
| ROC AUC Score | 1.00      |

📈 Only **1 false negative** out of 600 test samples.

---

## 🚀 How to Run the App Locally

### 🔧 Requirements

```bash
pip install flask pandas scikit-learn joblib
