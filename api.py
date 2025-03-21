from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import NewsScraper
import uvicorn
from typing import List, Dict, Any, Optional
import os

app = FastAPI(title="News Sentiment and TTS API",
              description="API for news extraction, sentiment analysis, and text-to-speech generation")

# Initialize news scraper
news_scraper = NewsScraper()

# Pydantic models for request/response
class CompanyRequest(BaseModel):
    company_name: str

class ArticleResponse(BaseModel):
    title: str
    summary: str
    sentiment: str
    topics: List[str]
    url: str

class SentimentDistribution(BaseModel):
    Positive: int = 0
    Negative: int = 0
    Neutral: int = 0

class ComparisonItem(BaseModel):
    comparison: str
    impact: str

class TopicOverlap(BaseModel):
    common_topics: List[str]
    unique_topics: List[str]

class ComparativeAnalysis(BaseModel):
    sentiment_distribution: Dict[str, int]
    coverage_differences: List[Dict[str, str]]
    topic_overlap: Dict[str, List[str]]
    final_sentiment_analysis: str

class CompanyNewsResponse(BaseModel):
    company: str
    articles: List[ArticleResponse]
    comparative_sentiment_score: ComparativeAnalysis
    final_sentiment_analysis: str

@app.post("/api/news_sentiment", response_model=CompanyNewsResponse)
async def get_news_sentiment(request: CompanyRequest):
    """
    Get news sentiment analysis for a company
    """
    try:
        result = news_scraper.process_company_news(request.company_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/text_to_speech")
async def generate_speech(request: CompanyRequest):
    """
    Generate Hindi TTS for company news summary
    """
    try:
        # First get the news sentiment
        result = news_scraper.process_company_news(request.company_name)
        
        # Create a summary text for TTS
        summary_text = f"Company: {result['company']}. "
        summary_text += f"Overall sentiment: {result['final_sentiment_analysis']} "
        
        # Add top 3 article summaries
        for i, article in enumerate(result['articles'][:3]):
            summary_text += f"Article {i+1}: {article['title']}. {article['summary']} "
        
        # Generate TTS
        output_file = f"{request.company_name.replace(' ', '_')}_summary.mp3"
        tts_file = news_scraper.text_to_hindi_speech(summary_text, output_file)
        
        return {"audio_file": tts_file, "text": summary_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)