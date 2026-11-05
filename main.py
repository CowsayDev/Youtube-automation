import os, requests, random, textwrap
from PIL import Image
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.generativeai as genai

# --- KEYS ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FIREFLY_CLIENT_ID = os.getenv("FIREFLY_CLIENT_ID")
FIREFLY_CLIENT_SECRET = os.getenv("FIREFLY_CLIENT_SECRET")
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_trending_funny_topic():
    prompt = """Aaj India me YouTube Shorts pe kya trending funny topic hai?
    Usi trending topic ko Maudaha ke Bagad Billa se jod ke 1 funny line de.
    Example: 'Neeraj Chopra ka gold' -> 'Bagad Billa ne bhala phenk ke Maudaha ki light tod di'
    Sirf 1 line de, 15 shabd me."""
    res = model.generate_content(prompt)
    return res.text.strip()

def get_adobe_token():
    url = "https://ims-na1.adobelogin.com/ims/token/v3"
    data = {"grant_type": "client_credentials", "client_id": FIREFLY_CLIENT_ID, "client_secret": FIREFLY_CLIENT_SECRET, "scope": "openid,AdobeID,firefly_api,ff_apis"}
    r = requests.post(url, data=data)
    return r.json()["access_token"]

def generate_firefly_image(prompt, token, filename):
    url = "https://firefly-api.adobe.io/v2/images/generate"
    headers = {"Authorization": f"Bearer {token}", "x-api-key": FIREFLY_CLIENT_ID, "Content-Type": "application/json"}
    payload = {"prompt": prompt + ", funny animated style, cartoon cat, Bundelkhandi gamcha, 4k, vibrant", "size": {"width": 1280, "height": 720}}
    r = requests.post(url, headers=headers, json=payload)
    img_url = r.json()["outputs"][0]["image"]["url"]
    with open(filename, "wb") as f:
        f.write(requests.get(img_url).content)
    return filename

def make_animated_video(topic):
    token = get_adobe_token()
    
    # 3 alag scene banayenge
    prompts = [f"{topic} scene 1", f"{topic} scene 2 funny reaction", f"{topic} scene 3 climax"]
    clips = []
    for i, p in enumerate(prompts):
        img_path = generate_firefly_image(p, token, f"scene_{i}.jpg")
        # Animated effect - Ken Burns zoom
        clip = ImageClip(img_path).set_duration(3)
        clip = clip.resize(lambda t: 1 + 0.1*t)  # Zoom animation
        clips.append(clip)

    full_clip = concatenate_videoclips(clips)
    
    # Funny animated text
    txt = TextClip(topic, fontsize=70, color='yellow', font='Arial-Bold', stroke_color='black', stroke_width=3, method='caption', size=(1000, None))
    txt = txt.set_position(('center','bottom')).set_duration(9)
    
    final = CompositeVideoClip([full_clip, txt])
    final.write_videofile("final_video.mp4", fps=24)
    return "final_video.mp4"

def upload_to_youtube(path, title):
    creds = Credentials(None, refresh_token=YT_REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token", client_id=YT_CLIENT_ID, client_secret=YT_CLIENT_SECRET, scopes=["https://www.googleapis.com/auth/youtube.upload"])
    youtube = build("youtube", "v3", credentials=creds)
    youtube.videos().insert(part="snippet,status", body={"snippet": {"title": f"{title} | Bagad Billa Funny", "description": f"{title}\n#trending #funny #maudaha #bagadbilla", "categoryId": "23"}, "status": {"privacyStatus": "public"}}, media_body=MediaFileUpload(path)).execute()

if __name__ == "__main__":
    topic = get_trending_funny_topic()
    print(f"TRENDING TOPIC: {topic}")
    video = make_animated_video(topic)
    upload_to_youtube(video, topic)
