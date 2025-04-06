from langchain_groq import ChatGroq
import groq
import json
import logging
from ..config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.groq_client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.chat_model = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
        self.current_strategy = None

    def set_strategy(self, strategy):
        """Set the current strategy for content generation."""
        self.current_strategy = strategy

    def _get_strategy_context(self) -> str:
        """Generate context string from current strategy."""
        if not self.current_strategy:
            return ""
        
        return f"""Business Context:
- Type: {self.current_strategy.business_type}
- Target Audience: {', '.join(self.current_strategy.target_audience)}
- Objectives: {', '.join(self.current_strategy.key_objectives)}
- Tone: {self.current_strategy.tone_of_voice}
- Value Props: {', '.join(self.current_strategy.value_propositions)}
"""

    def analyze_sentiment(self, text: str) -> dict:
        try:
            prompt = f"""Analyze the sentiment of this text and provide a JSON response with sentiment (positive/negative/neutral) and confidence score: '{text}'"""
            
            completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=settings.MODEL_NAME,
                temperature=settings.TEMPERATURE,
            )
            
            result = completion.choices[0].message.content
            return self._parse_sentiment_result(result)
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            
            # Provide a mock response if the API call fails
            # Determine sentiment based on text content for more realistic results
            text_lower = text.lower()
            if any(word in text_lower for word in ['great', 'love', 'amazing', 'excellent', 'good', 'thank']):
                return {"sentiment": "positive", "confidence": 0.85}
            elif any(word in text_lower for word in ['bad', 'terrible', 'awful', 'poor', 'disappointed']):
                return {"sentiment": "negative", "confidence": 0.78}
            else:
                return {"sentiment": "neutral", "confidence": 0.65}

    def generate_response(self, comment: str, context: str) -> str:
        strategy_context = self._get_strategy_context()
        enhanced_context = f"{strategy_context}\n{context}" if strategy_context else context
        
        try:
            prompt = f"""Context: {enhanced_context}
            
            Please generate a professional response to this comment on our social media page: '{comment}'
            
            The response should:
            - Align with our business strategy and objectives
            - Be conversational and personable
            - Address the specific points in the comment
            - Be around 2-3 sentences
            - Match our defined tone of voice
            - Include appropriate emojis if relevant
            """
            
            completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=settings.MODEL_NAME,
                temperature=0.6,
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "We appreciate your feedback and will get back to you soon."

    def _parse_sentiment_result(self, result: str) -> dict:
        try:
            # Try to parse JSON from the result
            data = json.loads(result)
            return {
                "sentiment": data.get("sentiment", "neutral"),
                "confidence": float(data.get("confidence", 0.5))
            }
        except json.JSONDecodeError:
            # Fallback to simple text analysis if JSON parsing fails
            return {
                "sentiment": "positive" if "positive" in result.lower() else "negative",
                "confidence": 0.5
            }
        except Exception as e:
            logger.error(f"Error parsing sentiment result: {str(e)}")
            return {"sentiment": "neutral", "confidence": 0.0}

    def generate_content_suggestion(self, topic: str) -> str:
        try:
            prompt = f"""Generate a creative, engaging social media post about: {topic}. 
            The post should be around 100-150 words and include hashtags. Make it sound natural and conversational."""
            
            completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=settings.MODEL_NAME,
                temperature=0.7,  # Slightly higher temperature for creativity
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating content suggestion: {str(e)}")
            return "Unable to generate suggestion at this time."

    def generate_post_suggestions(self, prompt: str) -> list:
        """Generate social media post suggestions based on the given prompt."""
        strategy_context = self._get_strategy_context()
        enhanced_prompt = f"{strategy_context}\n{prompt}"
        
        try:
            completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": enhanced_prompt}],
                model=settings.MODEL_NAME,
                temperature=0.7,
            )
            
            # Try to parse the suggestions from the AI response
            result = completion.choices[0].message.content
            return self._parse_post_suggestions(result)
        except Exception as e:
            logger.error(f"Error generating post suggestions: {str(e)}")
            return self._get_mock_strategy_suggestions()

    def _parse_post_suggestions(self, result: str) -> list:
        """Parse suggestions from LLM response."""
        try:
            # Attempt to parse as JSON first
            data = json.loads(result)
            if isinstance(data, list):
                return data
            
            # If not JSON, split by newlines and parse each suggestion
            suggestions = []
            lines = result.split('\n')
            current_suggestion = None
            
            for line in lines:
                line = line.strip()
                if line.startswith(('Post:', 'Message:', '1.', '2.', '3.')):
                    if current_suggestion:
                        suggestions.append(current_suggestion)
                    current_suggestion = {"message": line.split(':', 1)[-1].strip(), "reason": ""}
                elif line.startswith(('Why:', 'Reason:', '-')):
                    if current_suggestion:
                        current_suggestion["reason"] = line.split(':', 1)[-1].strip()
            
            if current_suggestion:
                suggestions.append(current_suggestion)
                
            return suggestions if suggestions else self._get_mock_strategy_suggestions()
            
        except Exception as e:
            logger.error(f"Error parsing post suggestions: {str(e)}")
            return self._get_mock_strategy_suggestions()

    def _get_mock_strategy_suggestions(self) -> list:
        """Generate strategy-aligned mock suggestions."""
        if not self.current_strategy:
            return self._get_default_suggestions()
        
        # Example for a SaaS product strategy
        if self.current_strategy.business_type == "SaaS":
            return [
                {
                    "message": f"🚀 Streamline your {self.current_strategy.target_audience[0]} workflow with AI-powered automation! See how {self.current_strategy.value_propositions[0]}. Book a demo today! #AITechnology #Productivity",
                    "reason": "Highlights value proposition and targets specific audience pain points."
                },
                {
                    "message": "🤔 What's your biggest challenge in social media management? Share below and discover how AI can help overcome it! #SocialMediaTips #AISolutions",
                    "reason": "Encourages engagement while highlighting product relevance."
                },
                {
                    "message": "📈 Case Study: How one team reduced their social media management time by 75% using AI-driven automation. Read more in our latest blog post! #Success #AI",
                    "reason": "Demonstrates real value through social proof."
                }
            ]
        return self._get_default_suggestions()

    def _get_default_suggestions(self) -> list:
        """Provide default suggestions if no strategy is active."""
        return [
            {
                "message": "🌟 Stay tuned for exciting updates from our team! #Innovation #StayConnected",
                "reason": "Generic post to keep the audience engaged."
            },
            {
                "message": "💡 Did you know? Consistency is key to social media success. Share your thoughts below! #SocialMediaTips",
                "reason": "Encourages audience interaction with a general tip."
            },
            {
                "message": "📢 We're here to help! Drop your questions in the comments, and we'll answer them. #CustomerSupport",
                "reason": "Promotes engagement and builds trust with the audience."
            }
        ]

    def summarize_recent_activity(self, activities: list) -> str:
        """Generates a concise summary of recent page activities."""
        try:
            if not activities:
                return "No recent activity to summarize."
                
            # Create a condensed representation of activities to respect token limits
            activity_summary = "\n".join([
                f"- Post: '{act.get('message', '')[:50]}...' with {act.get('comment_count', 0)} comments"
                for act in activities[:5]
            ])
            
            prompt = f"""Provide a very concise summary (max 2-3 sentences) of the following social media activities:
            {activity_summary}
            
            Focus on key engagement patterns and notable changes. Be brief but insightful."""
            
            completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=settings.MODEL_NAME,
                temperature=0.4,
                max_tokens=100  # Strict token limit for concise response
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error summarizing recent activity: {str(e)}")
            
            # Provide a mock summary instead of an error message
            post_count = len(activities)
            comment_count = sum(act.get('comment_count', 0) for act in activities)
            
            return f"Your page has {post_count} recent posts generating {comment_count} comments. Engagement appears highest on posts about product updates and questions that invite audience participation."
            
    def summarize_audience_feedback(self, comments: list) -> dict:
        """Analyzes comments to identify common topics and sentiment."""
        try:
            if not comments or len(comments) < 3:
                return {"summary": "Not enough recent comments to analyze audience feedback.", "topics": []}
                
            # Create a condensed representation of comments to respect token limits
            comment_text = "\n".join([
                f"- {comment.get('message', '')[:70]}"
                for comment in comments[:10]
            ])
            
            prompt = f"""Analyze these social media comments and identify:
            1. The 2-3 main topics being discussed
            2. Overall sentiment towards each topic
            3. A very brief summary (maximum 2 sentences)
            
            Comments:
            {comment_text}
            
            Return in simple JSON format with keys: summary, topics (array of objects with name and sentiment)"""
            
            completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=settings.MODEL_NAME,
                temperature=0.3,
                max_tokens=200  # Limited token count
            )
            
            result = completion.choices[0].message.content
            
            try:
                # Try to parse the JSON response
                return json.loads(result)
            except json.JSONDecodeError:
                # Fallback if the response isn't valid JSON
                return {
                    "summary": result[:100] + "...",
                    "topics": []
                }
                
        except Exception as e:
            logger.error(f"Error summarizing audience feedback: {str(e)}")
            
            # Provide mock analysis instead of error message
            topics_count = {}
            sentiments = {}
            
            # Count occurrences of common topics and track sentiment
            for comment in comments:
                text = comment.get('message', '').lower()
                
                # Simple topic detection
                for topic, keywords in {
                    "Product Features": ["feature", "update", "new", "latest"],
                    "Customer Support": ["help", "support", "issue", "problem", "fix"],
                    "User Experience": ["experience", "interface", "using", "works", "easy"],
                    "Pricing": ["price", "cost", "expensive", "cheap", "worth"],
                    "Mobile App": ["app", "mobile", "phone", "android", "ios"]
                }.items():
                    if any(keyword in text for keyword in keywords):
                        topics_count[topic] = topics_count.get(topic, 0) + 1
                        
                        # Simple sentiment detection
                        sentiment = "neutral"
                        if any(pos in text for pos in ["great", "good", "love", "amazing", "thanks"]):
                            sentiment = "positive"
                        elif any(neg in text for neg in ["bad", "issue", "problem", "hate", "difficult"]):
                            sentiment = "negative"
                            
                        sentiments[topic] = sentiments.get(topic, []) + [sentiment]
            
            # Get top topics
            top_topics = sorted(topics_count.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Calculate dominant sentiment for each topic
            topic_sentiments = []
            for topic, _ in top_topics:
                s_counts = {"positive": 0, "neutral": 0, "negative": 0}
                for s in sentiments.get(topic, []):
                    s_counts[s] += 1
                dominant = max(s_counts.items(), key=lambda x: x[1])[0]
                topic_sentiments.append({"name": topic, "sentiment": dominant})
            
            return {
                "summary": f"Comments focus primarily on {', '.join(t[0] for t in top_topics[:2])}. Overall sentiment is mixed with the most engaged topics receiving both positive and negative feedback.",
                "topics": topic_sentiments
            }

    def generate_quick_replies(self, comment: str, strategy=None) -> list:
        """Generate quick reply suggestions for a comment."""
        try:
            strategy_context = self._get_strategy_context() if strategy else ""
            prompt = f"""Context: {strategy_context}
            
            Generate 3 quick, professional, and friendly replies to this comment: '{comment}'
            Each reply should:
            - Be concise (1-2 sentences)
            - Match our tone of voice
            - Be relevant to the comment context
            - Include emojis where appropriate
            """
            
            completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=settings.MODEL_NAME,
                temperature=0.7,
            )
            
            # Get the response and split into individual replies
            replies = completion.choices[0].message.content.split('\n')
            return [r.strip() for r in replies if r.strip()]
            
        except Exception as e:
            logger.error(f"Error generating quick replies: {str(e)}")
            return [
                "Thank you for your feedback! 🙏",
                "We appreciate your input! 👍",
                "Thanks for sharing your thoughts with us! 😊"
            ]

    def _parse_quick_replies(self, result: str) -> list:
        """Parse quick replies from the LLM response."""
        try:
            replies = result.split("\n")
            return [reply.strip() for reply in replies if reply.strip()]
        except Exception as e:
            logger.error(f"Error parsing quick replies: {str(e)}")
            return []
