# Darwix AI Assessment Project

This project implements two AI-powered features for a Django web application:
1. Audio Transcription with Speaker Diarization
2. Blog Post Title Suggestions using NLP

## Features

### 1. Audio Transcription with Diarization
- Transcribes audio files to text
- Identifies different speakers in the conversation
- Supports multiple languages
- Returns structured JSON with speaker segments and timestamps

### 2. Blog Post Title Suggestions
- Generates multiple title suggestions for blog posts
- Uses OpenAI GPT-3.5 for intelligent title generation
- Has a fallback method that doesn't require API access
- Extracts key topics and sentences from content

## Prerequisites

- Python 3.8+
- Django 4.0+
- CUDA-capable GPU (recommended for faster transcription)
- HuggingFace account and API token
- OpenAI API key (optional, for better title suggestions)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd darwix-ai-assessment
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with:
```
HUGGINGFACE_API_KEY=your_huggingface_token
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_django_secret_key
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## API Endpoints

### 1. Audio Transcription

**Endpoint:** `/api/transcribe/`
**Method:** POST
**Authentication:** Required

**Request:**
- Content-Type: multipart/form-data
- Body:
  - `audio_file`: Audio file (mp3, wav, etc.)

**Response:**
```json
{
    "language": "en-US",
    "segments": [
        {
            "speaker": "SPEAKER_00",
            "start": 0.0,
            "end": 2.5,
            "text": "Hello, this is speaker one."
        },
        {
            "speaker": "SPEAKER_01",
            "start": 2.5,
            "end": 5.0,
            "text": "And this is speaker two."
        }
    ],
    "complete_transcript": "Hello, this is speaker one. And this is speaker two."
}
```

### 2. Blog Title Suggestions

**Endpoint:** `/api/suggest-titles/`
**Method:** POST
**Authentication:** Required

**Request:**
```json
{
    "content": "Your blog post content here...",
    "num_suggestions": 3
}
```

**Response:**
```json
{
    "suggestions": [
        "10 Ways to Improve Your Blog Writing Skills",
        "The Ultimate Guide to Effective Blogging",
        "Mastering the Art of Blog Writing: A Comprehensive Guide"
    ]
}
```

## Testing

Run the test suite:
```bash
python manage.py test
```

## Error Handling

The API endpoints handle various error cases:
- Missing or invalid audio files
- Authentication failures
- API key issues
- Processing errors

All errors return appropriate HTTP status codes and error messages.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

