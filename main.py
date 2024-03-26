from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import time
import requests
import json

api_key = '5457fbde-71b5-4368-a766-9ac0fa003122'
credentials_file = './services_acc.json'
user_email = 'roman-babaev@sharp-nation-417713.iam.gserviceaccount.com'
scopes = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    credentials_file, scopes=scopes, subject=user_email)

drive_service = build('drive', 'v3', credentials=credentials)

folder_id = '1468m8Nu6WjmnyTagHhNcLS_aPQIM43u5'

results = drive_service.files().list(
    q=f"'{folder_id}' in parents and mimeType contains 'video/'",
    spaces='drive',
    fields='nextPageToken, files(id, name, mimeType)',
    pageSize=100).execute()
items = results.get('files', [])

if not items:
    print('No video files found.')
else:
    print('Video links:')
    for item in items:
        file = drive_service.files().get(fileId=item['id'], fields='webContentLink').execute()
        download_url = file.get('webContentLink')

        import_data = {
            "url": download_url,
            "name": item['name'],
            "startDate": "2022-01-01T00:00:00Z",
            "endDate": "2022-01-01T01:00:00Z",
            "description": "Описание встречи",
            "participants": [
                {
                    "email": "example@example.com",
                    "role": "participant"
                }
            ]
        }

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key
        }
        response = requests.post('https://pasta.tldv.io/v1alpha1/meetings/import', headers=headers, json=import_data)

        # Проверка ответа
        if response.status_code == 200:
            print(f"Встреча '{item['name']}' успешно импортирована.")
            job_id = response.json()['jobId']
            time.sleep(60)
            response = requests.get(f'https://pasta.tldv.io/v1alpha1/meetings/{job_id}/transcript', headers=headers)
            print(response.json())
        else:
            print(f"Ошибка при импорте встречи '{item['name']}': {response.text}")
