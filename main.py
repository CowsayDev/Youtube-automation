import os
import requests
import random
import textwrap
import xml.etree.ElementTree as ET
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageSequenceClip
import numpy as np
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- KEYS ---
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")

def get_trending_topic():
    print("Trending topic le raha hu...")
    url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    try:
        r = requests.get(url, timeout=20)
        root = ET.fromstring(r.content)
        titles = [item.find('title').text for item in root.findall('.//item')[:15]]
        if not titles:
            raise ValueError("No titles")
        topic = random.choice(titles)
        print(f"Topic: {topic}")
        return topic
    except Exception as e:
        print(f"RSS Error: {e}, using fallback")
        return f"Breaking News Update {datetime.now().strftime('%d %B %I %p')}"

def create_animated_video(text, output="final.mp4"):
    print(f"Video bana raha hu: {text}")
    W, H = 720, 1280
    FPS = 24
    DURATION = 8
    TOTAL_FRAMES = FPS * DURATION

    bg_color = random.choice([
        (255, 193, 7), (33, 150, 243), (76, 175, 80), (233, 30, 99)
    ])

    frames = []
    try:
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 50)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 28)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    wrapped = textwrap.fill(text, width=20)

    for i in range(TOTAL_FRAMES):
        img = Image.new('RGB', (W, H), color=bg_color)
        draw = ImageDraw.Draw(img)

        # FIXED: bracket error yahan tha, ab sahi hai
        for _ in range(6):
            x = random.randint(0, W)
            y = (random.randint(0, H) + i * 5) % H
            draw.ellipse([x, y, x+20, y+20], fill=(255, 255, 255, 150))

        draw.rounded_rectangle([30, 80, W-30, 170], radius=20, fill="black")
        draw.text((W//2, 125), "🔥 TRENDING NEWS 🔥", font=font_small, fill="white", anchor="mm")

        draw.rounded_rectangle([30, 320, W-30, 900], radius=35, fill="white")
        draw.text((W//2, 600), wrapped, font=font_big, fill="black", anchor="mm", align="center")

        draw.text((W//2, 1080), datetime.now().strftime("%d %B | %I:%M %p IST"), font=font_small, fill="white", anchor="mm")

        frames.append(np.array(img))

    clip = ImageSequenceClip(frames, fps=FPS)
    clip.write_videofile(output, codec='libx264', audio=False, logger=None)
    print(f"Video ready: {output}")
    return output

def create_thumbnail(text):
    print("Thumbnail bana raha hu...")
    img = Image.new('RGB', (1280, 720), color=(255, 193, 7))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 65)
    except:
        font = ImageFont.load_default()

    wrapped = textwrap.fill(text, width=22)
    draw.rounded_rectangle([40, 40, 1240, 680], radius=40, fill="white")
    draw.text((640, 360), wrapped, font=font, fill="black", anchor="mm", align="center")
    img.save("thumbnail.jpg")
    return "thumbnail.jpg"

def upload_youtube(video_path, thumb_path, title):
    if not all([YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN]):
        raise ValueError("YouTube secrets missing!")

    creds = Credentials(
        None,
        refresh_token=YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YT_CLIENT_ID,
        client_secret=YT_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    youtube = build("youtube", "v3", credentials=creds)

    print(f"YouTube pe upload: {title}")
    resp = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title[:95],
                "description": f"{title}\n\nTrending news auto update. #Trending #News #Shorts #Viral #Maudaha",
                "categoryId": "25",
                "tags": ["trending", "news", "shorts"]
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(video_path, resumable=True)
    ).execute()

    video_id = resp["id"]
    print(f"Uploaded: https://youtu.be/{video_id}")

    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumb_path)
    ).execute()
    print("Thumbnail lag gaya!")

if __name__ == "__main__":
    topic = get_trending_topic()
    yt_title = f"{topic[:70]} | {datetime.now().strftime('%I:%M %p')} Update"
    video_file = create_animated_video(topic)
    thumb_file = create_thumbnail(topic)
    upload_youtube(video_file, thumb_file, yt_title)
