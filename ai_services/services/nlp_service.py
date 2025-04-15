import nltk
import openai
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

class BlogTitleSuggestionService:
    """Service for generating blog post title suggestions using NLP"""
    
    def __init__(self, openai_api_key=None):
        self.openai_api_key = openai_api_key
        self._setup_nltk()
        
    def _setup_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
    
    def _extract_key_topics(self, content, num_topics=5):
        """Extract key topics from blog post content using TF-IDF"""
        # Tokenize and preprocess
        stop_words = set(stopwords.words('english'))
        tokens = word_tokenize(content.lower())
        filtered_tokens = [w for w in tokens if w.isalnum() and w not in stop_words]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(max_features=100)
        tfidf_matrix = vectorizer.fit_transform([' '.join(filtered_tokens)])
        
        # Get feature names and scores
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        
        # Get top scoring words
        word_scores = list(zip(feature_names, scores))
        word_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [word for word, score in word_scores[:num_topics]]
    
    def _extract_key_sentences(self, content, num_sentences=2):
        """Extract key sentences from the content"""
        sentences = sent_tokenize(content)
        
        # If there are very few sentences, return the first one
        if len(sentences) <= num_sentences:
            return sentences
            
        # For longer content, extract the most representative sentences
        # (first sentence + sentences with key topics)
        key_topics = set(self._extract_key_topics(content))
        
        # Score sentences based on presence of key topics
        sentence_scores = []
        for sentence in sentences:
            sentence_tokens = set(word_tokenize(sentence.lower()))
            score = sum(1 for word in sentence_tokens if word in key_topics)
            sentence_scores.append((sentence, score))
        
        # Sort by score and get top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in sentence_scores[:num_sentences-1]]
        
        # Always include the first sentence as it often sets the topic
        if sentences[0] not in top_sentences:
            top_sentences = [sentences[0]] + top_sentences[:num_sentences-1]
            
        return top_sentences
    
    def _generate_title_with_openai(self, content, num_suggestions=3):
        """Generate title suggestions using OpenAI's API"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for this feature")
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Extract key sentences for summarization
        key_sentences = self._extract_key_sentences(content)
        summary = " ".join(key_sentences)
        
        # Prepare the prompt
        prompt = f"""Generate {num_suggestions} catchy, SEO-friendly title suggestions for a blog post with the following content summary:

Content Summary: {summary}

Guidelines:
- Titles should be engaging and clear
- Keep titles between 40-60 characters
- Make titles descriptive yet concise
- Each title should be unique in style or approach
- Format the response as a numbered list

Generate {num_suggestions} titles:"""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional blog title generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        # Parse the response to extract titles
        titles_text = response.choices[0].message.content.strip()
        
        # Extract individual titles from the numbered list
        titles = []
        for line in titles_text.split('\n'):
            if line.strip() and any(line.strip().startswith(f"{i}.") for i in range(1, num_suggestions+1)):
                # Remove number prefix and whitespace
                title = line.strip().split('.', 1)[1].strip()
                titles.append(title)
        
        # Ensure we have the expected number of titles
        while len(titles) < num_suggestions:
            titles.append(f"Suggested Title #{len(titles)+1}")
            
        return titles
    
    def _generate_title_without_api(self, content, num_suggestions=3):
        """Generate title suggestions without external API (fallback method)"""
        # Extract key topics and sentences
        key_topics = self._extract_key_topics(content, num_topics=7)
        key_sentences = self._extract_key_sentences(content, num_sentences=2)
        
        # Templates for title generation
        templates = [
            "How to {topic1} and {topic2} in {current_year}",
            "The Ultimate Guide to {topic1}: {topic2} and Beyond",
            "{num} Ways to Improve Your {topic1} with {topic2}",
            "{topic1} 101: Everything You Need to Know About {topic2}",
            "Why {topic1} Matters: The Importance of {topic2}",
            "Understanding {topic1}: A Comprehensive Guide to {topic2}",
            "The Future of {topic1}: Trends in {topic2} for {current_year}",
        ]
        
        import random
        from datetime import datetime
        
        suggestions = []
        used_templates = set()
        
        for _ in range(num_suggestions):
            # Select random topics
            topic1 = random.choice(key_topics)
            topic2 = random.choice([t for t in key_topics if t != topic1])
            
            # Select template avoiding duplicates if possible
            available_templates = [t for t in templates if t not in used_templates]
            if not available_templates:
                available_templates = templates
                
            template = random.choice(available_templates)
            used_templates.add(template)
            
            # Fill template
            title = template.format(
                topic1=topic1.capitalize(),
                topic2=topic2.capitalize(),
                num=random.choice([3, 5, 7, 10]),
                current_year=datetime.now().year
            )
            
            suggestions.append(title)
            
        return suggestions
    
    def generate_title_suggestions(self, content, num_suggestions=3):
        """
        Generate title suggestions for a blog post
        
        Args:
            content: Blog post content
            num_suggestions: Number of title suggestions to generate
            
        Returns:
            list: List of suggested titles
        """
        try:
            # Try using OpenAI API first
            if self.openai_api_key:
                return self._generate_title_with_openai(content, num_suggestions)
            else:
                # Fall back to simpler method if no API key
                return self._generate_title_without_api(content, num_suggestions)
                
        except Exception as e:
            # Emergency fallback if everything fails
            return [
                f"Blog Post Title Suggestion #{i+1}" 
                for i in range(num_suggestions)
            ]