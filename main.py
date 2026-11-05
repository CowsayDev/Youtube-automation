import os
import google.generativeai as genai
from gtts import gTTS
from moviepy.editor import ColorClip, AudioFileClip, TextClip, CompositeVideoClip

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 1. FEEDBACK READ
feedback_text = "Pehli video hai"
if os.path.exists("last_feedback.txt"):
    with open("last_feedback.txt", "r", encoding="utf-8") as f:
        feedback_text = f.read()

# 2. AI SE TITLE + HOOK + SCRIPT + HASHTAG EK SATH LENA
prompt = f"""
Feedback: '{feedback_text}'.
Mujhe ek viral YouTube Shorts ke liye 4 cheezein de, Hindi me, is format me:

TITLE: (60 character se kam, viral, curiosity wala)
HOOK_TEXT: (Video ke upar dikhne wala 3-4 shabd ka bada text, jaise '5G KA SACH!')
SCRIPT: (40 second ki full script, Hindi me)
HASHTAGS: (5 viral hashtags)

Topic trending hona chahiye India me.
"""

res = model.generate_content(prompt).text
print(res)

# 3. AI KE JAWAB KO ALAG-ALAG KARNA
try:
    title = res.split("TITLE:")[1].split("HOOK_TEXT:")[0].strip().replace('"', '').replace('*', '')[:90]
    hook = res.split("HOOK_TEXT:")[1].split("SCRIPT:")[0].strip().replace('"', '').replace('*', '')[:30]
    script = res.split("SCRIPT:")[1].split("HASHTAGS:")[0].strip()
    hashtags = res.split("HASHTAGS:")[1].strip()
except:
    title = "Aaj ka Viral Sach"
    hook = "VIRAL SACH!"
    script = res
    hashtags = "#shorts #viral #facts #trending #india"

print(f"Title: {title}")
print(f"Hook: {hook}")

# 4. AUDIO BANANA
tts = gTTS(text=script, lang='hi', slow=False)
tts.save("audio.mp3")
audio = AudioFileClip("audio.mp3")

# 5. VIDEO BANANA + UPAR BADA CAPTION LAGANA
bg = ColorClip(size=(1080, 1920), color=(10, 10, 10), duration=audio.duration)

try:
    txt_clip = TextClip(hook, fontsize=90, color='white', font='DejaVu-Sans-Bold', stroke_color='black', stroke_width=3, method='caption', size=(900, None))
    txt_clip = txt_clip.set_position(('center', 400)).set_duration(audio.duration)
    final_video = CompositeVideoClip([bg, txt_clip]).set_audio(audio)
except Exception as e:
    print(f"TextClip error {e}, making video without text")
    final_video = bg.set_audio(audio)

final_video.write_videofile("final_video.mp4", fps=24, codec='libx264', audio_codec='aac')

# 6. TITLE AUR DESCRIPTION SAVE KARNA
with open("title.txt", "w", encoding="utf-8") as f:
    f.write(title)

with open("desc.txt", "w", encoding="utf-8") as f:
    f.write(f"{script}\n\n{hashtags}")

with open("current_script.txt", "w", encoding="utf-8") as f:
    f.write(script)

print("Video ban gayi!")
