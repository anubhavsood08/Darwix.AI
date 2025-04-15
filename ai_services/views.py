import os
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .services.audio_service import AudioTranscriptionService
from .services.nlp_service import BlogTitleSuggestionService


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transcribe_audio(request):
    """
    API endpoint for audio transcription with speaker diarization
    
    Accepts audio file uploads and returns transcription with speaker identification
    """
    if 'audio_file' not in request.FILES:
        return Response({'error': 'No audio file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    audio_file = request.FILES['audio_file']
    
    # Save the uploaded file temporarily
    temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_audio', audio_file.name)
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    
    with open(temp_path, 'wb+') as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)
    
    try:
        # Create transcription service
        transcription_service = AudioTranscriptionService(
            huggingface_token=settings.HUGGINGFACE_API_KEY
        )
        
        # Process the audio file
        result = transcription_service.transcribe_audio(temp_path)
        
        # Clean up the temporary file
        os.remove(temp_path)
        
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return Response(
            {'error': f'Transcription failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def suggest_blog_titles(request):
    """
    API endpoint for generating blog post title suggestions
    
    Accepts blog content and returns suggested titles
    """
    try:
        # Get blog content from request data
        data = request.data
        
        if 'content' not in data:
            return Response(
                {'error': 'Blog content is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content = data['content']
        num_suggestions = data.get('num_suggestions', 3)
        
        # Create title suggestion service
        suggestion_service = BlogTitleSuggestionService(
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Generate title suggestions
        suggestions = suggestion_service.generate_title_suggestions(
            content=content,
            num_suggestions=num_suggestions
        )
        
        # Return the suggestions
        return Response({
            'suggestions': suggestions
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate title suggestions: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )