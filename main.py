import openai
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from config import YOUTUBE_API_KEY, OPENAI_API_KEY
import speech_recognition as sr

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak your query...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language="en-IN")
        print("✅ You said:", text)
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        return None

def get_text_input():
    return input("Enter your search query: ")

def search_youtube(query, api_key):
    print(f"\n🔍 Searching YouTube for: {query}")
    youtube = build("youtube", "v3", developerKey=api_key)
    published_after = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()

    try:
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=20,
            publishedAfter=published_after
        )
        response = request.execute()
    except Exception as e:
        print(f"❌ YouTube API error: {e}")
        return []

    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        videos.append({"title": title, "video_id": video_id})
    return videos

# Analyze titles using keyword-based scoring
def analyze_titles(videos):
    print("\n🎯 Analyzing top video titles (fallback logic)...")
    
    keywords = ['best', 'dsa', 'course', 'tutorial', 'beginner', 'guide', 'roadmap']
    scored_videos = []

    for video in videos:
        title = video['title'].lower()
        score = sum(1 for kw in keywords if kw in title)
        scored_videos.append((score, video))

    # Sort by score descending
    scored_videos.sort(reverse=True, key=lambda x: x[0])

    if scored_videos and scored_videos[0][0] > 0:
        top_video = scored_videos[0][1]
        return f"{top_video['title']} - https://youtu.be/{top_video['video_id']}"
    else:
        print("\n⚠️ No highly relevant video found. Showing top 3:")
        for i, video in enumerate(videos[:3]):
            print(f"{i+1}. {video['title']} - https://youtu.be/{video['video_id']}")
        return "Failed to get highly relevant recommendation."

def main():
    input_type = input("Input type? (1) Voice (2) Text: ")
    if input_type.strip() == "1":
        query = get_voice_input()
        if not query:
            return
    else:
        query = get_text_input()

    videos = search_youtube(query, YOUTUBE_API_KEY)
    if not videos:
        print("❌ No videos found.")
        return

    best_video = analyze_titles(videos)
    print("\n✅ Best Video Recommendation:\n", best_video)

if __name__ == "__main__":
    main()
