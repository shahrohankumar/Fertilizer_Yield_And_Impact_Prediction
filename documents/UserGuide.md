# User Guide: Fertilizer Impact Prediction

## Overview
This guide explains how to use the Fertilizer Impact Prediction platform to predict crop yields and understand fertilizer impacts.

---

## Steps to Use
1. **Open the Application**:
   - Run the Flask server and open `http://127.0.0.1:5000/` in your browser.

2. **Input Details**:
   - Fill in the form with:
     - Soil Type
     - Weather
     - Fertilizer Type
     - Fertilizer Amount
     - Crop Type

3. **Submit the Form**:
   - Click the **Predict** button to analyze.

4. **View Results**:
   - Predicted crop yield will appear on the screen.
   - Fertilizer effect description will be fetched from the Gemini API.

---

## Common Issues
- **Server Not Running**: Ensure Flask is running using `python app.py`.
- **API Errors**: Check your Gemini API key and internet connection.
- **Empty Results**: Verify input values are valid.

---

## Contact
For assistance, reach out to:
- **Email**: [Rohansah@gmail.com]
