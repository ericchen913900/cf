import os
import uuid
from flask import Flask, request, jsonify

# --- README ---
# This file contains a simple Flask-based backend service for the CoolSpace AI project.
# Its primary purpose is to provide an API endpoint for the mobile app
# to upload the 3D room scan data.

# Initialize the Flask application.
app = Flask(__name__)

# Define the directory where uploaded scans will be stored.
# In a production environment, this would be a cloud storage bucket (e.g., AWS S3).
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """A simple index route to confirm the server is running."""
    return "CoolSpace AI Backend Service is running."

@app.route('/api/v1/upload_scan', methods=['POST'])
def upload_scan():
    """
    API endpoint to receive 3D scan data from the mobile app.
    The data is expected to be in the request body.
    """
    # Check if data is present in the request.
    if not request.data:
        return jsonify({"error": "No data provided in the request."}), 400

    # The mobile app sends the OBJ data as a raw string in the request body.
    scan_data = request.data

    # Generate a unique identifier for this scan.
    scan_id = str(uuid.uuid4())
    filename = f"scan_{scan_id}.obj"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        # Save the uploaded data to a file.
        with open(filepath, 'wb') as f:
            f.write(scan_data)
    except IOError as e:
        print(f"Error saving file: {e}")
        return jsonify({"error": "Failed to save scan data on the server."}), 500

    # In a real application, we would now trigger the CFD analysis pipeline asynchronously.
    # This is done by adding a job to a task queue (e.g., Celery).
    # The worker process would then handle the long-running simulation.
    # Example: run_cfd_simulation.delay(scan_id, filepath)
    # For this PoC, we just confirm the upload.
    print(f"Successfully received and saved scan {scan_id} to {filepath}. A CFD job would be queued.")

    # Return a success response to the client.
    return jsonify({
        "message": "Scan uploaded successfully.",
        "scan_id": scan_id,
        "filename": filename,
        "size_bytes": len(scan_data)
    }), 201

if __name__ == '__main__':
    # Run the app. In a production environment, use a proper WSGI server like Gunicorn.
    app.run(debug=True, port=5000)
