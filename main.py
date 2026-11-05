import os
import time
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- KEYS - naam bilkul CAPITAL me ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")

genai.configure(api_key=GEMINI_API_KEY)

# --- TUNE JO BOLA WAHI MODEL ---
# Video Generation Model
VIDEO_MODEL_NAME = "gemini-omni-1.1-flash"
TEXT_MODEL_NAME = "gemini-omni-1.1-flash"

def get_topic():
    model = genai.GenerativeModel(TEXT_MODEL_NAME)
    prompt = "Maudaha ke Bagad Billa ke liye 1 trending funny YouTube Shorts topic de, 15 shabd me, Bundelkhandi desi comedy. Sirf topic."
    res = model.generate_content(prompt)
    return res.text.strip()

def generate_video_with_omni(topic):
    print(f"Omni 1.1 Flash se video bana raha hu: {topic}")
    
    model = genai.GenerativeModel(VIDEO_MODEL_NAME)
    
    # Omni 1.1 Flash Video Prompt
    prompt = f"""
    Create a 8 second funny vertical video: {topic}
    Character: Maudaha ka Bagad Billa, a funny desi cat wearing Bundelkhandi red gamcha
    Style: funny, animated, vibrant, 9:16 vertical, trending YouTube Shorts style
    """

    # Video generation call
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "video/mp4"}
    )

    # Video save
    with open("final.mp4", "wb") as f:
        f.write(response.parts[0].inline_data.data)
    
    print("Video ban gayi: final.mp4")
    return "final.mp4"

def upload_to_youtube(path, title):
    creds = Credentials(
        None, refresh_token=YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YT_CLIENT_ID, client_secret=YT_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    youtube = build("youtube", "v3", credentials=creds)
    
    youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title[:90], "description": f"{title}\n\n#maudaha #bagadbilla", "categoryId": "23"},
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(path)
    ).execute()
    print("YouTube pe upload ho gaya!")

if __name__ == "__main__":
    topic = get_topic()
    print(f"Topic: {topic}")
    video = generate_video_with_omni(topic)
    upload_to_youtube(video, topic)
