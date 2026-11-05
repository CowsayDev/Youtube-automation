import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds = Credentials(
    None,
    refresh_token=os.getenv("YT_REFRESH_TOKEN"),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=os.getenv("YT_CLIENT_ID"),
    client_secret=os.getenv("YT_CLIENT_SECRET"),
    scopes=['https://www.googleapis.com/auth/youtube.upload']
)

youtube = build('youtube', 'v3', credentials=creds)

with open("title.txt", "r", encoding="utf-8") as f:
    title = f.read().strip()

with open("desc.txt", "r", encoding="utf-8") as f:
    desc = f.read().strip()

media = MediaFileUpload("final_video.mp4", mimetype="video/mp4", resumable=True)

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": title,
            "description": desc,
            "tags": ["shorts", "viral", "facts", "india", "trending"],
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    },
    media_body=media
)

response = request.execute()
print(f"Uploaded Successfully: https://www.youtube.com/watch?v={response['id']}")
