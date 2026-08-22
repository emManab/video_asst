import os

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except Exception:
    PYDUB_AVAILABLE = False

DOWNLOAD_DIR = "downloades"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


class TextTranscript:
    """Wraps an already-fetched plain-text transcript from the YT Transcript API."""
    def __init__(self, text: str):
        self.text = text


def fetch_youtube_transcript(url: str):
    """
    Try to pull captions from YouTube via the official transcript endpoint.
    Works from any IP - no download needed, no 403 errors.
    Returns the transcript string, or None if unavailable.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        import re

        vid_id = None
        m = re.search(r"(?:v=|youtu\.be/|/v/|/embed/)([A-Za-z0-9_-]{11})", url)
        if m:
            vid_id = m.group(1)

        if not vid_id:
            return None

        try:
            entries = YouTubeTranscriptApi.get_transcript(vid_id, languages=["en"])
        except Exception:
            entries = YouTubeTranscriptApi.get_transcript(vid_id)

        transcript = " ".join(e["text"] for e in entries)
        print(f"Fetched YouTube transcript ({len(transcript)} chars) - skipping audio download.")
        return transcript

    except Exception as e:
        print(f"Transcript API failed ({e}). Will try audio download.")
        return None


def download_youtube_audio(url: str) -> str:
    if not YT_DLP_AVAILABLE:
        raise RuntimeError("yt-dlp is not installed.")
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    
    # Try different client spoofs if YouTube blocks the cloud IP with a 403 Forbidden
    client_configs = [
        {"youtube": {"player_client": ["android", "web"]}},
        {"youtube": {"player_client": ["ios"]}},
        {"youtube": {"player_client": ["android_vr"]}},
        {} # fallback to default
    ]
    
    last_error = None
    for config in client_configs:
        try:
            print(f"Trying yt-dlp config: {config}")
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_path,
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "192"}],
                "quiet": True,
                "extractor_args": config
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
                return filename
        except Exception as e:
            last_error = e
            if "403" not in str(e) and "Forbidden" not in str(e):
                # If it's a legitimate error (e.g., video deleted), don't retry
                pass 
    
    error_msg = str(last_error)
    if "403" in error_msg or "Forbidden" in error_msg:
        raise RuntimeError(
            "YouTube's anti-bot system blocked the server from downloading this video. \n\n"
            "**💡 How to fix this:** \n"
            "1. Use a YouTube video that has **Closed Captions (CC) enabled** (the app will grab the text instantly without downloading).\n"
            "2. Or, download the video to your computer and use the **'Upload File'** tab!"
        )
    elif "unavailable" in error_msg.lower():
        raise RuntimeError("This YouTube video is unavailable, private, or has been deleted. Please check the link.")
    else:
        raise RuntimeError(f"Failed to process YouTube video. Reason: {last_error}")


def convert_to_wav(input_path: str) -> str:
    """Convert any local audio/video file to WAV using ffmpeg directly (more robust than pydub for video files)."""
    import subprocess
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    cmd = [
        "ffmpeg", "-y",          # -y = overwrite output if exists
        "-i", input_path,
        "-vn",                   # drop video stream, audio only
        "-acodec", "pcm_s16le",  # WAV format
        "-ar", "16000",          # 16kHz sample rate for Whisper
        "-ac", "1",              # mono
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Fallback to pydub
        if PYDUB_AVAILABLE:
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(output_path, format="wav")
        else:
            raise RuntimeError(f"ffmpeg failed (code {result.returncode}): {result.stderr[-500:]}")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    if not PYDUB_AVAILABLE:
        raise RuntimeError("pydub is not available.")
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks


def process_input(source: str):
    """
    Smart router:
    - YouTube URL: Try transcript API first (avoids 403). Falls back to audio download.
    - Local file: Convert to WAV and chunk for Whisper.
    Returns TextTranscript (already transcribed) or list of audio chunk paths.
    """
    is_url = source.startswith("http://") or source.startswith("https://")

    if is_url:
        print("Detected YouTube URL. Trying Transcript API first...")
        text = fetch_youtube_transcript(source)
        if text:
            return TextTranscript(text)
        print("Falling back to audio download...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready - {len(chunks)} chunk(s) created.")
    return chunks
