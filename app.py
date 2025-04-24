from flask import Flask, jsonify, request
from flask_cors import CORS  # Import Flask-CORS
import analyze_compliance as ac
import os
import json
from werkzeug.utils import secure_filename
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/api/compliance', methods=['POST'])
def get_compliance():
    try:
        req_body = request.get_json()
        reference_file = req_body['referenceFile']
        user_training_file = req_body('userTrainingFile')
        
        final_df = ac.compute_compliance(reference_file, user_training_file)
        
        # Convert DataFrame to JSON string
        json_data = final_df.to_json(orient='records')

        return jsonify(json_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Return error with appropriate status code
    
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/upload_with_json', methods=['POST'])
def upload_with_json():
    
    print('request: ', request.form)
    print('request form: ', request.form['project'])
    print('files: ', request.files)
    if 'project' not in request.form:
        return jsonify({'error': 'Missing jsonData'}), 400

    try:
        json_data = request.form['project']
        print("Received JSON data:", json_data)
    except json.JSONDecodeError:
        print('traceback: ', traceback.format_exc())
        return jsonify({'error': 'Invalid jsonData format'}), 400

    if 'referenceFile' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    reference_file = request.files.get('referenceFile')
    training_files = request.files.getlist('trainingFiles')
    # print('train_file: ', train_file[0])
    # print('train_file: ', train_file[1])
    print('ref file: ', reference_file)

    if reference_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if reference_file:
        filename = secure_filename(reference_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        reference_file.save(file_path)
        # return jsonify({'message': f'File "{filename}" uploaded successfully', 'received_json': json_data}), 200
    
    if training_files:
        uploaded_training_files = []
        for train_file in training_files:
            train_filename = secure_filename(train_file.filename)
            train_filepath = os.path.join(app.config['UPLOAD_FOLDER'], train_filename)
            train_file.save(train_filepath)
            uploaded_training_files.append(train_filename)
            print(f"Training file saved to: {train_filepath}")
        return jsonify({'message': 'Files uploaded successfully',
                        'reference_file': reference_file.filename if reference_file else None,
                        'training_files': uploaded_training_files}), 200
    elif reference_file:
        return jsonify({'message': 'Reference file uploaded successfully, no training files found',
                        'reference_file': reference_file}), 200

    return jsonify({'error': 'Failed to upload file'}), 500

if __name__ == '__main__':
    app.run(debug=True)  # Set debug=False for production