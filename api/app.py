from flask import Flask, jsonify, request
from flask_cors import CORS  # Import Flask-CORS
import analyze_compliance as ac

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/api/compliance', methods=['POST'])
def get_compliance():
    try:
        req_body = request.get_json()
        
        final_df = ac.compute_compliance()
        
        # Convert DataFrame to JSON string
        json_data = final_df.to_json(orient='records')

        return jsonify(json_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Return error with appropriate status code

if __name__ == '__main__':
    app.run(debug=True)  # Set debug=False for production