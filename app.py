import streamlit as st
import pandas as pd
import json
import base64
import os
import time
from utils import NewsScraper
import threading

# Set page configuration
st.set_page_config(
    page_title="News Sentiment & TTS Analysis",
    page_icon="📰",
    layout="wide"
)

# Initialize news scraper (only once)
@st.cache_resource
def get_news_scraper():
    return NewsScraper()

news_scraper = get_news_scraper()

# App title and description
st.title("📰 Company News Sentiment & Text-to-Speech Analysis")
st.markdown("""
This application analyzes news sentiment for a company and generates a text-to-speech summary in Hindi.
Enter a company name to see sentiment analysis across multiple news sources.
""")

# Helper functions
def get_audio_player(audio_file):
    """Return HTML for audio player"""
    audio_bytes = open(audio_file, 'rb').read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    return f'<audio controls><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>'

def get_sentiment_color(sentiment):
    """Return color based on sentiment"""
    if sentiment == "Positive":
        return "green"
    elif sentiment == "Negative":
        return "red"
    else:
        return "gray"

# Direct API functions
def get_news_sentiment(company_name):
    """Call the news scraper directly instead of via API"""
    result = news_scraper.process_company_news(company_name)
    return result

def generate_speech(company_name, result):
    """Generate Hindi TTS for company news summary"""
    # Create a summary text for TTS
    summary_text = f"Company: {result['company']}. "
    summary_text += f"Overall sentiment: {result['final_sentiment_analysis']} "
    
    # Add top 3 article summaries
    for i, article in enumerate(result['articles'][:3]):
        summary_text += f"Article {i+1}: {article['title']}. {article['summary']} "
    
    # Generate TTS
    output_file = f"{company_name.replace(' ', '_')}_summary.mp3"
    tts_file = news_scraper.text_to_hindi_speech(summary_text, output_file)
    
    return {"audio_file": tts_file, "text": summary_text}

# Company selection input
company_options = ["Apple", "Microsoft", "Google", "Amazon", "Tesla", "Facebook", "Netflix", "IBM", "Intel", "AMD"]
company_name = st.selectbox("Select a company or type a custom name:", options=company_options)

# Allow custom company input
custom_company = st.text_input("Or enter a custom company name:")
if custom_company:
    company_name = custom_company

# Create a layout with columns
col1, col2 = st.columns([2, 1])

# Process button
if st.button("Analyze News Sentiment"):
    # Show loading spinner
    with st.spinner("Fetching and analyzing news articles..."):
        try:
            # Call news sentiment function directly
            result = get_news_sentiment(company_name)
            
            # Display results in the first column
            with col1:
                st.subheader(f"News Analysis for {result['company']}")
                
                # Display sentiment distribution
                sentiment_dist = result['comparative_sentiment_score']['sentiment_distribution']
                
                # Create sentiment distribution chart
                sentiment_df = pd.DataFrame({
                    'Sentiment': list(sentiment_dist.keys()),
                    'Count': list(sentiment_dist.values())
                })
                
                st.bar_chart(sentiment_df.set_index('Sentiment'))
                
                # Display final sentiment analysis
                st.markdown(f"### Overall Sentiment")
                st.markdown(f"**{result['final_sentiment_analysis']}**")
                
                # Display news articles
                st.markdown("### News Articles")
                for i, article in enumerate(result['articles']):
                    with st.expander(f"{i+1}. {article['title']} ({article['sentiment']})"):
                        st.markdown(f"**Summary:** {article['summary']}")
                        st.markdown(f"**Topics:** {', '.join(article['topics'])}")
                        st.markdown(f"**Sentiment:** <span style='color:{get_sentiment_color(article['sentiment'])}'>{article['sentiment']}</span>", unsafe_allow_html=True)
                        st.markdown(f"[Read full article]({article['url']})")
            
            # Display comparative analysis in the second column
            with col2:
                st.subheader("Comparative Analysis")
                
                # Topic overlap
                st.markdown("#### Topic Analysis")
                topic_overlap = result['comparative_sentiment_score']['topic_overlap']
                
                if topic_overlap['common_topics']:
                    st.markdown("**Common Topics:**")
                    for topic in topic_overlap['common_topics']:
                        st.markdown(f"- {topic}")
                
                if topic_overlap['unique_topics']:
                    st.markdown("**Unique Topics:**")
                    for topic in topic_overlap['unique_topics']:
                        st.markdown(f"- {topic}")
                
                # Coverage differences
                st.markdown("#### Coverage Comparison")
                for comparison in result['comparative_sentiment_score']['coverage_differences']:
                    st.markdown(f"**Comparison:** {comparison['comparison']}")
                    st.markdown(f"**Impact:** {comparison['impact']}")
                    st.markdown("---")
                
                # Generate Text to Speech
                st.subheader("Hindi Text-to-Speech")
                with st.spinner("Generating Hindi speech..."):
                    # Call TTS function directly
                    tts_result = generate_speech(company_name, result)
                    
                    st.markdown("#### Audio Summary")
                    st.markdown(get_audio_player(tts_result['audio_file']), unsafe_allow_html=True)
                    
                    with st.expander("Show Text Summary"):
                        st.markdown(tts_result['text'])
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Add information about JSON output structure
with st.expander("View Sample JSON Output Structure"):
    sample_json = {
        "company": "Tesla",
        "articles": [
            {
                "title": "Tesla's New Model Breaks Sales Records",
                "summary": "Tesla's latest EV sees record sales in Q3...",
                "sentiment": "Positive",
                "topics": ["Electric Vehicles", "Stock Market", "Innovation"]
            },
            {
                "title": "Regulatory Scrutiny on Tesla's Self-Driving Tech",
                "summary": "Regulators have raised concerns over Tesla's self-driving software...",
                "sentiment": "Negative",
                "topics": ["Regulations", "Autonomous Vehicles"]
            }
        ],
        "comparative_sentiment_score": {
            "sentiment_distribution": {
                "Positive": 1,
                "Negative": 1,
                "Neutral": 0
            },
            "coverage_differences": [
                {
                    "comparison": "Article 1 highlights Tesla's strong sales, while Article 2 discusses regulatory issues.",
                    "impact": "The first article boosts confidence in Tesla's market growth, while the second raises concerns about future regulatory hurdles."
                }
            ],
            "topic_overlap": {
                "common_topics": ["Electric Vehicles"],
                "unique_topics": ["Stock Market", "Innovation", "Regulations", "Autonomous Vehicles"]
            }
        },
        "final_sentiment_analysis": "Tesla's latest news coverage is mixed. Potential stock volatility expected."
    }
    
    st.json(sample_json)

# Footer
st.markdown("---")
st.markdown("News Sentiment and TTS Analysis App | Data Science Intern Project")