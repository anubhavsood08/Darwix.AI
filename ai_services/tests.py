import os
import tempfile
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from .services.audio_service import AudioTranscriptionService
from .services.nlp_service import BlogTitleSuggestionService

class AudioTranscriptionServiceTest(TestCase):
    def setUp(self):
        self.service = AudioTranscriptionService(
            huggingface_token=os.getenv('HUGGINGFACE_API_KEY')
        )
        
    def test_convert_audio_to_wav(self):
        # Create a temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.mp3') as temp_audio:
            temp_audio.write(b'dummy audio data')
            temp_audio.flush()
            
            # Convert to WAV
            wav_path = self.service._convert_audio_to_wav(temp_audio.name)
            
            # Check if file exists and has .wav extension
            self.assertTrue(os.path.exists(wav_path))
            self.assertTrue(wav_path.endswith('.wav'))
            
            # Clean up
            os.remove(wav_path)
    
    def test_detect_language(self):
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav') as temp_audio:
            temp_audio.write(b'dummy audio data')
            temp_audio.flush()
            
            # Detect language
            language = self.service._detect_language(temp_audio.name)
            
            # Should return a string
            self.assertIsInstance(language, str)
            self.assertTrue(len(language) > 0)

class BlogTitleSuggestionServiceTest(TestCase):
    def setUp(self):
        self.service = BlogTitleSuggestionService(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
    def test_extract_key_topics(self):
        content = """
        Machine learning is transforming the way we analyze data.
        Deep learning models have achieved remarkable results in various fields.
        Artificial intelligence is becoming increasingly important in our daily lives.
        """
        
        topics = self.service._extract_key_topics(content)
        
        # Should return a list of topics
        self.assertIsInstance(topics, list)
        self.assertTrue(len(topics) > 0)
        self.assertTrue(all(isinstance(topic, str) for topic in topics))
    
    def test_generate_title_suggestions(self):
        content = """
        In this article, we explore the latest developments in artificial intelligence.
        We discuss how machine learning is changing various industries and what the future holds.
        The impact of AI on society and the economy is also examined.
        """
        
        suggestions = self.service.generate_title_suggestions(content, num_suggestions=3)
        
        # Should return the requested number of suggestions
        self.assertIsInstance(suggestions, list)
        self.assertEqual(len(suggestions), 3)
        self.assertTrue(all(isinstance(title, str) for title in suggestions))

class APITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Add authentication token if needed
        
    def test_transcribe_audio_endpoint(self):
        # Create a dummy audio file
        audio_file = SimpleUploadedFile(
            "test.mp3",
            b"dummy audio data",
            content_type="audio/mpeg"
        )
        
        response = self.client.post(
            '/api/transcribe/',
            {'audio_file': audio_file},
            format='multipart'
        )
        
        # Should return 401 if not authenticated
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_suggest_titles_endpoint(self):
        data = {
            'content': 'Test blog post content',
            'num_suggestions': 3
        }
        
        response = self.client.post(
            '/api/suggest-titles/',
            data,
            format='json'
        )
        
        # Should return 401 if not authenticated
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
