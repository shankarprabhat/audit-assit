from flask import Flask, jsonify, request
from flask_cors import CORS  # Import Flask-CORS
import analyze_compliance as ac
import os
import json
from werkzeug.utils import secure_filename
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
    
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

async def upload_with_json(request):
    
    print('in upload with json request: ', request.form)
    print('request form: ', request.form['project'])
    print('files: ', request.files)
    if 'project' not in request.form:
        return {'error': 'Missing jsonData'}

    try:
        json_data = request.form['project']
        print("Received JSON data:", json_data)
    except json.JSONDecodeError:
        print('traceback: ', traceback.format_exc())
        return {'error': 'Invalid jsonData format'}

    print('returned from 0')
    if 'referenceFile' not in request.files:
        return {'error': 'No file part in the request'}

    reference_file = request.files.get('referenceFile')
    training_files = request.files.getlist('userTrainingFiles')
    # print('train_file: ', train_file[0])
    # print('train_file: ', train_file[1])
    # print('returned from 1')
    print('ref file: ', reference_file)
    print('train file: ', training_files)

    if reference_file.filename == '':
        return {'error': 'No Reference file selected'}

    # print('returned from 2')
    if reference_file:
        filename = secure_filename(reference_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        reference_file.save(file_path)
        # return jsonify({'message': f'File "{filename}" uploaded successfully', 'received_json': json_data}), 200
    
    # print('returned from 3')
    # print('training_files: ', training_files)
    if training_files[0].filename == '':
        return {'error': 'No Training file selected'}
    if training_files:   
        uploaded_training_files = []
        for train_file in training_files:
            train_filename = secure_filename(train_file.filename)
            train_filepath = os.path.join(app.config['UPLOAD_FOLDER'], train_filename)
            train_file.save(train_filepath)
            uploaded_training_files.append(train_filename)
            print(f"Training file saved to: {train_filepath}")
        return {'message': 'Files uploaded successfully',
                        'reference_file': reference_file.filename if reference_file else None,
                        'training_files': uploaded_training_files}
    elif reference_file:
        return {'message': 'Reference file uploaded successfully, no training files found',
                        'reference_file': reference_file}

    return {'error': 'Failed to upload file'}

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/api/compliance', methods=['POST'])
async def get_compliance():
    try:
        try:
            print('request: ', request)
            print('header: ', request.headers)
            content_type = request.headers.get('Content-Type')
            print('content_type: ', content_type)
        except:
            print('traceback: ', traceback.format_exc())
            return jsonify({'error': 'Invalid jsonData format'}), 400
        try:
            if content_type == 'application/json':
                print('content is json')
                req_body = request.get_json()
                print('req_body: ', req_body)
                reference_file = req_body['referenceFile']
                user_training_file = req_body['userTrainingFile']
                
            elif content_type.startswith('multipart/form-data'):
                print('content is multipart/form-data')
                upload_file_path = await upload_with_json(request)

                if 'error' in upload_file_path:
                    return jsonify({'error': upload_file_path['error']}), 400
                
                print('upload_file_path: ', upload_file_path)
                reference_file = upload_file_path['reference_file']
                user_training_file = upload_file_path['training_files']            
        except:
            print('traceback: ', traceback.format_exc())
            return jsonify({'error': 'Invalid jsonData format'}), 400
        
        final_df = ac.compute_compliance(reference_file, user_training_file)
        
        # Convert DataFrame to JSON string
        json_data = final_df.to_json(orient='records')

        return jsonify(json_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Return error with appropriate status code

if __name__ == '__main__':
    app.run(debug=True)  # Set debug=False for production