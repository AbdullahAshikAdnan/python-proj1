from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configure Drop Cowboy API credentials
dropcowboy_team_id = "acb1088b-e24d-4c61-bb83-cfb335d71892"
dropcowboy_secret_key = "48db8265-f632-418b-b4f3-eb8c24aaef58"
dropcowboy_api_url = "https://api.dropcowboy.com/v1/rvm"

# Configure JotForm API credentials
jotformApiKey = "27f50030f5db987ecbf9f985f47076ec"
jotformFormId = "231365209409051"
jotformApiUrl = "https://api.jotform.com"

# Define route for JotForm webhook notification
@app.route("/jotform-webhook", methods=["POST"])
def jotform_webhook():
    print("Received form data:", request.form)

    # Extract form data from JotForm submission
    area_code = request.form.get("input_5_area")
    phone_number = request.form.get("input_5_phone")
    voicemail_file_url = "https://drive.google.com/u/0/uc?id=1mg5_sXZNN8U0dYTw9aumoz16wJQhgaw6&export=download"
    
    # Log that the form submission is received
    print("JotForm submission received.")

    # Check if file was received
    if not voicemail_file_url:
        print("File not received")
        return jsonify({"error": "File not received"}), 400

    # Perform any necessary validation on the form data

    # Call function to schedule RVM
    try:
        schedule_rvm(phone_number, voicemail_file_url)
        return jsonify({"message": "RVM scheduled successfully"}), 200
    except Exception as e:
        print("Failed to schedule RVM:", str(e))
        return jsonify({"error": "Failed to schedule RVM"}), 500

def schedule_rvm(phone_number, voicemail_file_url):
    # Download the file from the provided URL
    response = requests.get(voicemail_file_url)
    response.raise_for_status()
    file_content = response.content
    
    # Set request headers and parameters
    headers = {
        "X-TeamID": dropcowboy_team_id,
        "X-SecretKey": dropcowboy_secret_key,
        "Content-Type": "application/json", 
    }
    
    # Hardcode the foreign_id
    foreign_id = "my_unique_foreign_id"

    # Prepare the payload for Drop Cowboy API
    payload = {
        "team_id": dropcowboy_team_id,
        "secret": dropcowboy_secret_key,
        "audio_url": voicemail_file_url,
        "audio_type": "mp3",
        "phone_number": phone_number,
        "foreign_id": "foreign_id",  # Replace with your system's ID
    }

    # Make the API request to Drop Cowboy to schedule RVM
    try:
        response = requests.post(dropcowboy_api_url, headers=headers, files={"voicemail": file_content}, data=payload)
        response.raise_for_status()
        print("RVM sent:", response.json())
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to send RVM: " + str(e))

if __name__ == "__main__":
    app.run(port=3000)
