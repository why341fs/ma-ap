# Local Voice Chat with Gemma (No API keys needed!)
# Uses: Whisper (tiny) for STT + pyttsx3 for TTS + Ollama for LLM

import whisper
import pyttsx3
import requests
import json
import pyaudio
import wave
import tempfile
import os

# Initialize Whisper (tiny model - smallest and fastest)
print("Loading Whisper tiny model...")
stt_model = whisper.load_model("tiny")

# Initialize TTS
tts_engine = pyttsx3.init()

# Set TTS voice (optional - customize here)
voices = tts_engine.getProperty('voices')
# List available voices
print("\nAvailable voices:")
for idx, voice in enumerate(voices):
    print(f"{idx}: {voice.name}")

# Choose voice (0 for male, 1 for female typically on Windows)
voice_choice = input("\nChoose voice number (0-{}, or press Enter for default): ".format(len(voices)-1))
if voice_choice.strip():
    tts_engine.setProperty('voice', voices[int(voice_choice)].id)

# Set speech rate (default 200, lower = slower, higher = faster)
tts_engine.setProperty('rate', 180)

def record_audio(duration=5):
    """Record audio from microphone"""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    p = pyaudio.PyAudio()
    
    print(f"\n🎤 Recording for {duration} seconds...")
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("✅ Recording finished!")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    wf = wave.open(temp_file.name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return temp_file.name

def transcribe_audio(audio_file):
    """Convert speech to text using Whisper"""
    print("🔄 Transcribing...")
    result = stt_model.transcribe(audio_file)
    return result["text"]

def chat_with_ollama(text, model="gemma-arabic"):
    """Send text to Ollama and get response"""
    print(f"💬 You said: {text}")
    print("🤔 Gemma is thinking...")
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": text,
            "stream": False
        }
    )
    
    return response.json()["response"]

def speak(text):
    """Convert text to speech"""
    print(f"🔊 Gemma says: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

def main():
    print("\n" + "="*60)
    print("🎙️  LOCAL VOICE CHAT WITH GEMMA")
    print("="*60)
    print("\n✨ Everything runs locally - no API keys needed!")
    print("📝 Using: Whisper tiny + pyttsx3 + Ollama")
    print("\n" + "="*60 + "\n")
    
    while True:
        try:
            # Record audio
            audio_file = record_audio(duration=5)
            
            # Transcribe
            text = transcribe_audio(audio_file)
            os.unlink(audio_file)  # Delete temp file
            
            if not text.strip():
                print("❌ Couldn't hear anything. Try again!\n")
                continue
            
            # Check for exit command
            if "bye" in text.lower() or "exit" in text.lower() or "quit" in text.lower():
                speak("Goodbye!")
                break
            
            # Get response from Gemma
            response = chat_with_ollama(text)
            
            # Speak response
            speak(response)
            
            print("\n" + "-"*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()
