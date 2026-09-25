import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from analyzer import analyze_resume, extract_text_from_pdf

app = Flask(__name__)

# Enable CORS for cross-origin requests from Frontend
CORS(app, resources={r"/*": {"origins": "*"}})

# Upload directory configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify backend status.
    """
    return jsonify({
        "status": "online",
        "message": "SkillGap AI Resume Analyzer Backend is running smoothly!"
    }), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Endpoint to process uploaded resume PDF and return skill gap analysis.
    """
    # 1. Validation: Check if file exists in request
    if 'file' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 2. Get target role from form data (default: Data Analyst)
    target_role = request.form.get('role', 'Data Analyst')

    # 3. Save uploaded PDF temporarily
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    
    try:
        file.save(filepath)

        # 4. Extract text using NLP core engine
        extracted_text = extract_text_from_pdf(filepath)

        if not extracted_text.strip():
            return jsonify({"error": "Could not extract text from PDF. Ensure it contains selectable text."}), 400

        # 5. Run Skill Gap Analysis logic
        analysis_result = analyze_resume(extracted_text, target_role=target_role)

        # 6. Clean up: Delete local PDF after extraction
        if os.path.exists(filepath):
            os.remove(filepath)

        return jsonify(analysis_result), 200

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": f"An error occurred during processing: {str(e)}"}), 500

if __name__ == '__main__':
    # Run development server on port 5000
    app.run(debug=True, host='127.0.0.1', port=5000)