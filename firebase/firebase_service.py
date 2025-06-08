import firebase_admin
from firebase_admin import credentials
import os
from google.auth.transport.requests import Request
import requests
import json
from datetime import datetime
from google.oauth2 import service_account

class FirebaseService:
    firebase_cert_path = r'firebase\data\firebase-adminsdk.json'
    project_id = "my-capstone-smt6"

    if not os.path.exists(firebase_cert_path):
        raise Exception(f"File Firebase Admin SDK tidak ditemukan di path: {firebase_cert_path}")

    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_cert_path)
        firebase_admin.initialize_app(cred)

    @staticmethod
    def get_access_token():
        scopes = ['https://www.googleapis.com/auth/firebase.messaging']
        credentials_obj = service_account.Credentials.from_service_account_file(
            FirebaseService.firebase_cert_path, scopes=scopes)
        credentials_obj.refresh(Request())
        return credentials_obj.token

    @staticmethod
    def send_notification(title, body, topic="user_baru", data=None):
        access_token = FirebaseService.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }
        if data is None:
            data = {
                "isRead": "false",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        message_payload = {
            "message": {
                "topic": topic,
                "notification": {
                    "title": title,
                    "body": body
                },
                "data": data
            }
        }

        url = f"https://fcm.googleapis.com/v1/projects/{FirebaseService.project_id}/messages:send"
        response = requests.post(url, headers=headers, data=json.dumps(message_payload))

        if response.status_code == 200:
            print("✅ Notifikasi berhasil dikirim:", response.json())
        else:
            print("❌ Error kirim notifikasi:", response.status_code, response.text)
