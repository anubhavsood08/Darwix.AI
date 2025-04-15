import os
import json
import speech_recognition as sr
from pydub import AudioSegment

class AudioTranscriptionService:
    """Service for transcribing audio files with basic speaker segmentation"""
    
    def __init__(self, huggingface_token=None):
        self.huggingface_token = huggingface_token
        
    def _convert_audio_to_wav(self, audio_path):
        """Convert audio file to wav format for processing"""
        audio = AudioSegment.from_file(audio_path)
        temp_wav = os.path.join(os.path.dirname(audio_path), 'temp.wav')
        audio.export(temp_wav, format='wav')
        return temp_wav
    
    def _detect_language(self, audio_path):
        """Detect the language of the audio"""
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            
        try:
            # Using Google's service to detect language
            language = recognizer.recognize_google(audio, show_all=True)
            if language and 'alternative' in language:
                return language.get('language', 'en-US')
        except:
            pass
        
        return 'en-US'  # Default to English if detection fails
    
    def transcribe_audio(self, audio_path):
        """
        Transcribe audio file with basic segmentation
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            dict: JSON-serializable dictionary with transcription results
        """
        # Convert audio to WAV format (if needed)
        wav_path = self._convert_audio_to_wav(audio_path)
        
        try:
            # Detect language
            language = self._detect_language(wav_path)
            
            # Transcribe using Google Speech Recognition
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio = recognizer.record(source)
                
            text = recognizer.recognize_google(audio)
            
            # Create a simple segment
            result = {
                'language': language,
                'segments': [
                    {
                        'speaker': 'SPEAKER_00',
                        'start': 0.0,
                        'end': len(AudioSegment.from_wav(wav_path)) / 1000.0,
                        'text': text
                    }
                ],
                'complete_transcript': text
            }
            
            # Clean up temporary WAV file
            os.remove(wav_path)
            
            return result
        
        except Exception as e:
            # Clean up and raise error
            if os.path.exists(wav_path):
                os.remove(wav_path)
            raise Exception(f"Transcription failed: {str(e)}")