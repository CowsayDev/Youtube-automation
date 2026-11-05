import os
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 1. Pichli video ka script padhna
try:
    with open("current_script.txt", "r", encoding="utf-8") as f:
        last_script = f.read()[:500]
except:
    last_script = "Pehli video hai"

# 2. YouTube se pichli video ke views lena
try:
    creds = Credentials(
        None,
        refresh_token=os.getenv("YT_REFRESH_TOKEN"),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.getenv("YT_CLIENT_ID"),
        client_secret=os.getenv("YT_CLIENT_SECRET"),
        scopes=['https://www.googleapis.com/auth/youtube.readonly']
    )
    youtube = build('youtube', 'v3', credentials=creds)
    req = youtube.search().list(part="snippet", forMine=True, type="video", order="date", maxResults=1).execute()
    last_title = req['items'][0]['snippet']['title'] if req['items'] else "No video yet"
except Exception as e:
    print(f"YouTube read error: {e}")
    last_title = "No video yet"

# 3. Gemini se feedback mangna
prompt = f"""
Pichli video ka title tha: '{last_title}'.
Pichli video ki script thi: '{last_script}'.
Mujhe agli video ke liye 3 line me feedback do. Batao ki Title ko aur viral kaise banau, Hook ko aur tez kaise karu, aur Script ko aur engaging kaise karu. Hindi me jawab do.
"""

try:
    feedback = model.generate_content(prompt).text
except Exception as e:
    feedback = f"Agli video me hook aur tez rakho. Title me curiosity badhao. {e}"

# 4. Feedback ko save karna taaki agli baar main.py use padh sake
with open("last_feedback.txt", "w", encoding="utf-8") as f:
    f.write(feedback)

print("Feedback saved:")
print(feedback)
