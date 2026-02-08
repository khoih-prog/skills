# /// script
# dependencies = ["openai", "yt-dlp"]
# ///

import os
import argparse
import subprocess
import shutil
import re
from datetime import datetime
from openai import OpenAI

def setup_env():
    """Load API keys from environment"""
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        exit(1)

def extract_audio(input_file, output_audio):
    print(f"🎬 Extracting audio from {input_file}...")
    # Use ffmpeg from path
    cmd = [
        "ffmpeg", "-i", input_file, "-vn",
        "-acodec", "libmp3lame", "-q:a", "4", "-y",
        output_audio
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install ffmpeg.")
        exit(1)
    except subprocess.CalledProcessError:
        print("Error: FFmpeg failed to process the video.")
        exit(1)

def transcribe_audio(audio_file, output_srt, output_txt):
    print("🗣️ Transcribing audio with Whisper...")
    client = OpenAI()
    
    try:
        with open(audio_file, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=f, 
                response_format="srt"
            )
        with open(output_srt, "w", encoding="utf-8") as f:
            f.write(transcript)
            
        with open(audio_file, "rb") as f:
            txt = client.audio.transcriptions.create(
                model="whisper-1", 
                file=f, 
                response_format="text"
            )
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(txt)
        
        return txt
    except Exception as e:
        print(f"Error during transcription: {e}")
        exit(1)

def analyze_content(transcript_text):
    print("🧠 Analyzing content with GPT-4...")
    client = OpenAI()
    
    prompt = f"""
    Analyze the following video transcript and generate YouTube metadata.
    
    TRANSCRIPT:
    {transcript_text[:15000]}... (truncated)
    
    OUTPUT FORMAT:
    1. Title (Catchy, SEO-optimized)
    2. Description (Summary + Timestamps if possible)
    3. Tags (Comma separated)
    4. Thumbnail Prompt (For AI image generator)
    
    Be creative and professional.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during analysis: {e}")
        return "Analysis failed."

def generate_thumbnail(prompt, output_file):
    print(f"🎨 Generating thumbnail...")
    
    possible_paths = [
        "../nano-banana-pro/scripts/generate_image.py", 
        os.path.join(os.getcwd(), "skills/nano-banana-pro/scripts/generate_image.py"),
        os.path.expanduser("~/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py")
    ]
    
    skill_path = None
    for p in possible_paths:
        if os.path.exists(p):
            skill_path = p
            break
            
    if not skill_path:
        print("⚠️ Nano Banana Pro skill not found. Skipping thumbnail.")
        return

    # Use uv to run the other script (it will handle its own deps if configured)
    cmd = [
        "uv", "run", skill_path,
        "--prompt", prompt,
        "--filename", output_file,
        "--resolution", "4K"
    ]
    
    api_key = os.getenv("NANO_BANANA_KEY")
    if api_key:
        cmd.extend(["--api-key", api_key])
        
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("⚠️ Thumbnail generation failed.")

def main():
    parser = argparse.ArgumentParser(description="YouTube AI Editor")
    parser.add_argument("--input", help="Path to input video file")
    parser.add_argument("--url", help="YouTube URL to download")
    args = parser.parse_args()

    setup_env()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"output_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    video_path = args.input
    
    if args.url:
        print(f"📥 Downloading from URL: {args.url}")
        video_path = os.path.join(output_dir, "downloaded_video.mp4")
        
        if not re.match(r'^https?://', args.url):
            print("Error: Invalid URL")
            return

        # Use python-yt-dlp or subprocess yt-dlp (if installed via pip)
        # Since we added yt-dlp to dependencies, we can use it via module or CLI
        # Using CLI via 'uv run yt-dlp' or assuming it's in path after pip install might be tricky
        # Better to use the library directly or assume 'yt-dlp' binary is available.
        # Let's try subprocess 'yt-dlp' first (user needs it installed), fallback to library if needed.
        # Actually, adding 'yt-dlp' to dependencies allows us to import it!
        
        try:
            import yt_dlp
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'outtmpl': video_path,
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([args.url])
        except Exception as e:
             print(f"Error: Download failed using yt_dlp library: {e}")
             return
    
    if not video_path or not os.path.exists(video_path):
        print("Error: Video file not found.")
        return

    audio_path = os.path.join(output_dir, "audio.mp3")
    extract_audio(video_path, audio_path)
    
    srt_path = os.path.join(output_dir, "subtitles.srt")
    txt_path = os.path.join(output_dir, "transcript.txt")
    transcript_text = transcribe_audio(audio_path, srt_path, txt_path)
    
    metadata = analyze_content(transcript_text)
    metadata_path = os.path.join(output_dir, "metadata.md")
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(metadata)
    
    thumbnail_prompt = "A high-tech futuristic abstract background representing AI"
    for line in metadata.split('\n'):
        if "Thumbnail Prompt" in line:
            parts = line.split(":", 1)
            if len(parts) > 1:
                thumbnail_prompt = parts[1].strip()
            break
            
    thumbnail_path = os.path.join(output_dir, "thumbnail.png")
    generate_thumbnail(thumbnail_prompt, thumbnail_path)

    print(f"✅ All done! Check the '{output_dir}' folder.")

if __name__ == "__main__":
    main()
