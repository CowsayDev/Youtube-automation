import os, random, math, numpy as np
from google import genai
from gtts import gTTS
from PIL import Image, ImageDraw
from moviepy.editor import AudioFileClip, VideoClip, CompositeVideoClip, TextClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

client = genai.Client()

# 1. TRENDING
trending = random.choice(["ISRO ka naya mission", "Virat Kohli ka record", "AI ne duniya badal di", "Gaon me hua chamatkar", "Paisa hi sab kuch hai?", "Dost ne dhoka de diya"])
print(f"Trending: {trending}")

# 2. SCRIPT - Maudaha ka Bagad Billa style
prompt = f"""
Trending: {trending}
Maudaha ka Bagad Billa style me 30 sec ki emotional Hindi script banao.
Character Bagad Billa camera se baat kar raha hai.
Pehle 2 sec me Hook: 'Bhai ruk ja...'
Script 70 words, dil ko chhu jaye.
Format:
TITLE: [title]
SCRIPT: [script]
"""
res = client.models.generate_content(model='gemini-1.5-flash',contents=prompt).text
title = "Bhai Ruk Ja Ye Sun Le!"
script = res
try:
    title = res.split("TITLE:")[1].split("SCRIPT:")[0].strip()
    script = res.split("SCRIPT:")[1].strip()
except: pass

open("title.txt","w",encoding="utf-8").write(title)
open("desc.txt","w",encoding="utf-8").write(f"{title}\n\n{script}\n\n#MaudahaKaBagadBilla #Shorts")
open("current_script.txt","w",encoding="utf-8").write(script)

# 3. VOICE - Free
tts = gTTS(text=script, lang='hi', slow=False)
tts.save("voice.mp3")
audio = AudioFileClip("voice.mp3")
duration = audio.duration + 0.5

# 4. FREE ANIMATION - Yahi Maudaha wala jugaad hai
# Tumhe ek baar apni Bagad Billa ki photo ko GitHub me 'character.png' naam se upload karna hai
# Agar nahi hai to ye code khud ek cartoon bana dega
try:
    base_img = Image.open("character.png").convert("RGB").resize((800, 800))
except:
    # Fallback - Agar photo nahi mili to ek aag ka gola bana do
    base_img = Image.new("RGB", (800, 800), (20, 20, 40))
    d = ImageDraw.Draw(base_img)
    d.ellipse([150, 150, 650, 650], fill=(255, 150, 0), outline=(255, 220, 0), width=10)
    # Aankh
    d.ellipse([280, 300, 350, 380], fill=(255,255,255))
    d.ellipse([450, 300, 520, 380], fill=(255,255,255))
    d.ellipse([305, 330, 335, 360], fill=(0,0,0))
    d.ellipse([475, 330, 505, 360], fill=(0,0,0))

W, H = 1080, 1920
# Background - Gaon jaisa
bg = Image.new("RGB", (W, H), (30, 80, 30))
bg_draw = ImageDraw.Draw(bg)
bg_draw.rectangle([0, 1400, W, H], fill=(120, 70, 20)) # Zameen

def make_frame(t):
    frame = bg.copy()
    # Character hilna - upar neeche (Body Bob)
    bob = int(math.sin(t * 4) * 15)
    # Muh khulna-band hona - jab voice chal rahi hai
    mouth_open = int(abs(math.sin(t * 8)) * 30) if t < duration - 0.5 else 5
    # Aankh jhapakna - har 3 sec me
    blink = 1 if (t % 3) < 0.15 else 0

    char = base_img.copy()
    # Muh banao - character ke neeche
    draw = ImageDraw.Draw(char)
    # Muh ko mita kar naya muh banao
    draw.ellipse([320, 550, 480, 550 + mouth_open + 10], fill=(0,0,0))
    if blink:
        draw.rectangle([280, 300, 520, 380], fill=(255,150,0)) # Aankh band

    # Character ko frame me chipkao
    frame.paste(char, (140, 600 + bob))
    # Upar Title
    return np.array(frame)

video = VideoClip(make_frame, duration=duration)
# Title Text
txt = TextClip(title, fontsize=65, color='yellow', size=(950, None), method='caption', align='center', font='DejaVu-Sans-Bold')
txt = txt.set_position(('center', 200)).set_duration(duration)
# Neeche Subscribe
sub = TextClip("SUBSCRIBE KARO 👇", fontsize=55, color='white', font='DejaVu-Sans-Bold')
sub = sub.set_position(('center', 1750)).set_duration(duration)

final = CompositeVideoClip([video, txt, sub]).set_audio(audio)
final.write_videofile("final_video.mp4", fps=24, codec="libx264", audio_codec="aac")
print("Free Animated Video Ban Gayi!")

# 5. YOUTUBE UPLOAD - Free
creds = Credentials(None, refresh_token=os.getenv("YT_REFRESH_TOKEN"), token_uri='https://oauth2.googleapis.com/token', client_id=os.getenv("YT_CLIENT_ID"), client_secret=os.getenv("YT_CLIENT_SECRET"), scopes=['https://www.googleapis.com/auth/youtube.upload'])
youtube = build('youtube','v3', credentials=creds)
body = {"snippet": {"title": title, "description": open("desc.txt").read(), "tags": ["MaudahaKaBagadBilla","Shorts"], "categoryId": "22"}, "status": {"privacyStatus": "public"}}
youtube.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload("final_video.mp4")).execute()
print("Upload Ho Gaya!")
