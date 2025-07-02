import speech_recognition as sr
import pyaudio
import wave
import os
import sys
from datetime import datetime
import json

class SpeechToTextTranscriber:
    def _init_(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        print("Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        print("Calibration complete.")
    
    def transcribe_microphone(self, duration=None, language='en-US'):
        """
        Transcribe speech from microphone input
        
        Args:
            duration (int): Maximum duration to listen (None for indefinite)
            language (str): Language code for recognition
        
        Returns:
            str: Transcribed text
        """
        print(f"\nListening for speech (language: {language})...")
        if duration:
            print(f"Recording for {duration} seconds...")
        else:
            print("Say something! (Press Ctrl+C to stop)")
        
        try:
            with self.microphone as source:
                if duration:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=duration)
                else:
                    audio = self.recognizer.listen(source, timeout=1)
            
            print("Processing speech...")
            
            # Try different recognition engines
            engines = [
                ('Google', lambda: self.recognizer.recognize_google(audio, language=language)),
                ('Sphinx (offline)', lambda: self.recognizer.recognize_sphinx(audio)),
            ]
            
            for engine_name, recognize_func in engines:
                try:
                    print(f"Trying {engine_name}...")
                    text = recognize_func()
                    print(f"✓ Transcription successful with {engine_name}")
                    return text
                except sr.UnknownValueError:
                    print(f"✗ {engine_name} could not understand the audio")
                    continue
                except sr.RequestError as e:
                    print(f"✗ {engine_name} error: {e}")
                    continue
            
            return "Could not transcribe audio with any engine"
            
        except sr.WaitTimeoutError:
            return "No speech detected within timeout period"
        except KeyboardInterrupt:
            print("\nRecording stopped by user")
            return "Recording cancelled"
        except Exception as e:
            return f"Error during recording: {str(e)}"
    
    def transcribe_audio_file(self, file_path, language='en-US'):
        """
        Transcribe speech from an audio file
        
        Args:
            file_path (str): Path to audio file
            language (str): Language code for recognition
        
        Returns:
            str: Transcribed text
        """
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' not found"
        
        print(f"\nTranscribing audio file: {file_path}")
        print(f"Language: {language}")
        
        try:
            with sr.AudioFile(file_path) as source:
                # Read the entire audio file
                audio = self.recognizer.record(source)
            
            print("Processing audio file...")
            
            # Try different recognition engines
            engines = [
                ('Google', lambda: self.recognizer.recognize_google(audio, language=language)),
                ('Sphinx (offline)', lambda: self.recognizer.recognize_sphinx(audio)),
            ]
            
            for engine_name, recognize_func in engines:
                try:
                    print(f"Trying {engine_name}...")
                    text = recognize_func()
                    print(f"✓ Transcription successful with {engine_name}")
                    return text
                except sr.UnknownValueError:
                    print(f"✗ {engine_name} could not understand the audio")
                    continue
                except sr.RequestError as e:
                    print(f"✗ {engine_name} error: {e}")
                    continue
            
            return "Could not transcribe audio file with any engine"
            
        except Exception as e:
            return f"Error processing audio file: {str(e)}"
    
    def record_audio_to_file(self, filename, duration=10, sample_rate=44100):
        """
        Record audio from microphone and save to file
        
        Args:
            filename (str): Output filename
            duration (int): Recording duration in seconds
            sample_rate (int): Sample rate for recording
        """
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        
        p = pyaudio.PyAudio()
        
        print(f"\nRecording audio for {duration} seconds...")
        print("Speak now!")
        
        try:
            stream = p.open(format=format,
                          channels=channels,
                          rate=sample_rate,
                          input=True,
                          frames_per_buffer=chunk)
            
            frames = []
            for i in range(0, int(sample_rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Save audio to file
            wf = wave.open(filename, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            print(f"Audio saved to: {filename}")
            
        except Exception as e:
            print(f"Error during recording: {str(e)}")
            p.terminate()
    
    def save_transcript(self, text, filename=None):
        """
        Save transcribed text to file
        
        Args:
            text (str): Text to save
            filename (str): Optional filename (auto-generated if None)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcript_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Transcript generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                f.write(text)
            
            print(f"Transcript saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error saving transcript: {str(e)}")
            return None

def print_menu():
    """Print the main menu options"""
    print("\n" + "="*50)
    print("    SPEECH-TO-TEXT TRANSCRIPTION TOOL")
    print("="*50)
    print("1. Transcribe from microphone (live)")
    print("2. Transcribe from audio file")
    print("3. Record audio and transcribe")
    print("4. List supported audio formats")
    print("5. Test microphone")
    print("6. Exit")
    print("="*50)

def list_audio_formats():
    """List supported audio formats"""
    print("\nSupported audio formats:")
    print("- WAV (.wav)")
    print("- FLAC (.flac)")
    print("- AIFF (.aiff)")
    print("- Note: For other formats (MP3, MP4, etc.), install pydub and ffmpeg")

def test_microphone():
    """Test microphone functionality"""
    print("\nTesting microphone...")
    try:
        r = sr.Recognizer()
        mic = sr.Microphone()
        
        print("Available microphones:")
        for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  {i}: {mic_name}")
        
        print("\nSay something to test your microphone...")
        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=5, phrase_time_limit=3)
        
        print("Microphone test successful!")
        
    except Exception as e:
        print(f"Microphone test failed: {str(e)}")

def get_language_choice():
    """Get language choice from user"""
    languages = {
        '1': ('en-US', 'English (US)'),
        '2': ('en-GB', 'English (UK)'),
        '3': ('es-ES', 'Spanish'),
        '4': ('fr-FR', 'French'),
        '5': ('de-DE', 'German'),
        '6': ('it-IT', 'Italian'),
        '7': ('pt-BR', 'Portuguese (Brazil)'),
        '8': ('ja-JP', 'Japanese'),
        '9': ('ko-KR', 'Korean'),
        '10': ('zh-CN', 'Chinese (Mandarin)')
    }
    
    print("\nSelect language:")
    for key, (code, name) in languages.items():
        print(f"{key}. {name}")
    
    choice = input("Enter choice (default: 1): ").strip() or '1'
    
    if choice in languages:
        return languages[choice][0]
    else:
        print("Invalid choice, using English (US)")
        return 'en-US'

def main():
    """Main application loop"""
    print("Initializing Speech-to-Text Transcriber...")
    
    try:
        transcriber = SpeechToTextTranscriber()
    except Exception as e:
        print(f"Error initializing transcriber: {str(e)}")
        print("Make sure you have installed: pip install speechrecognition pyaudio")
        return
    
    while True:
        try:
            print_menu()
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                # Live microphone transcription
                language = get_language_choice()
                duration_input = input("Enter recording duration in seconds (press Enter for continuous): ").strip()
                duration = int(duration_input) if duration_input.isdigit() else None
                
                transcript = transcriber.transcribe_microphone(duration=duration, language=language)
                print(f"\nTranscript:\n{'-'*30}")
                print(transcript)
                print('-'*30)
                
                if input("\nSave transcript to file? (y/N): ").lower() == 'y':
                    filename = input("Enter filename (press Enter for auto-generated): ").strip() or None
                    transcriber.save_transcript(transcript, filename)
            
            elif choice == '2':
                # Audio file transcription
                file_path = input("Enter path to audio file: ").strip()
                language = get_language_choice()
                
                transcript = transcriber.transcribe_audio_file(file_path, language=language)
                print(f"\nTranscript:\n{'-'*30}")
                print(transcript)
                print('-'*30)
                
                if input("\nSave transcript to file? (y/N): ").lower() == 'y':
                    filename = input("Enter filename (press Enter for auto-generated): ").strip() or None
                    transcriber.save_transcript(transcript, filename)
            
            elif choice == '3':
                # Record and transcribe
                duration_input = input("Enter recording duration in seconds (default: 10): ").strip()
                duration = int(duration_input) if duration_input.isdigit() else 10
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_filename = f"recording_{timestamp}.wav"
                
                transcriber.record_audio_to_file(audio_filename, duration=duration)
                
                if input("Transcribe the recorded audio? (Y/n): ").lower() != 'n':
                    language = get_language_choice()
                    transcript = transcriber.transcribe_audio_file(audio_filename, language=language)
                    print(f"\nTranscript:\n{'-'*30}")
                    print(transcript)
                    print('-'*30)
                    
                    if input("\nSave transcript to file? (y/N): ").lower() == 'y':
                        filename = input("Enter filename (press Enter for auto-generated): ").strip() or None
                        transcriber.save_transcript(transcript, filename)
            
            elif choice == '4':
                list_audio_formats()
            
            elif choice == '5':
                test_microphone()
            
            elif choice == '6':
                print("Thank you for using Speech-to-Text Transcriber!")
                break
            
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
        
        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            continue

if __name__ == "__main__":
    main()
