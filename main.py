import streamlit as st
from pytrends.request import TrendReq
from openai import OpenAI
import pandas as pd
import os
import time
from typing import Optional, Dict, Any

# ========================
# 🛠️ CONFIGURATION
# ========================
@st.cache_resource
def configure_openai():
    """Initialize OpenAI client with multiple fallback options"""
    try:
        # Try Streamlit secrets first
        if hasattr(st, 'secrets') and "OPENAI_API_KEY" in st.secrets:
            return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Fallback to environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return OpenAI(api_key=api_key)
        
        # Final fallback to user input
        return None
    except Exception as e:
        st.error(f"API configuration failed: {str(e)}")
        return None

def get_api_key_input():
    """Handle API key input in sidebar"""
    with st.sidebar:
        st.markdown("### 🔑 API Configuration")
        temp_key = st.text_input(
            "Enter OpenAI API Key:", 
            type="password",
            help="Your API key is not stored and only used for this session"
        )
        if temp_key:
            return OpenAI(api_key=temp_key)
    return None

# ========================
# 🖥️ PAGE SETUP
# ========================
st.set_page_config(
    page_title="AI SEO Specialist",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .tool-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🔍 AI SEO Specialist</h1>
    <p>Boost your SEO with AI-driven keyword research and content generation!</p>
</div>
""", unsafe_allow_html=True)

# Initialize OpenAI client
client = configure_openai()
if not client:
    client = get_api_key_input()

# ========================
# 🛠️ TOOL FUNCTIONS
# ========================
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_keyword_trends(keyword: str) -> Optional[pd.DataFrame]:
    """Fetch related queries from Google Trends with error handling"""
    try:
        with st.spinner("🔍 Analyzing search trends..."):
            # Add delay to avoid rate limiting
            time.sleep(1)
            
            pytrends = TrendReq(
                hl='en-US', 
                tz=330,
                timeout=(10, 25),
                retries=2,
                backoff_factor=0.1
            )
            
            # Build payload with error handling
            pytrends.build_payload([keyword], timeframe='today 12-m')
            
            # Get related queries
            related_queries = pytrends.related_queries()
            
            if keyword in related_queries and related_queries[keyword]['top'] is not None:
                df = related_queries[keyword]['top']
                if not df.empty:
                    # Add some mock metrics for demonstration
                    df['estimated_volume'] = df['value'] * 100
                    df['difficulty'] = (df['value'] / df['value'].max() * 100).round().astype(int)
                    return df
            
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Trends API error: {str(e)}")
        # Return mock data for demonstration
        return create_mock_keyword_data(keyword)

def create_mock_keyword_data(keyword: str) -> pd.DataFrame:
    """Create mock keyword data when API fails"""
    mock_data = {
        'query': [
            f'{keyword} tips',
            f'{keyword} guide',
            f'{keyword} strategies',
            f'{keyword} best practices',
            f'{keyword} tools'
        ],
        'value': [100, 85, 70, 60, 45],
        'estimated_volume': [10000, 8500, 7000, 6000, 4500],
        'difficulty': [65, 58, 72, 55, 48]
    }
    return pd.DataFrame(mock_data)

def generate_meta_description(topic: str, tone: str, target_length: int = 155) -> Optional[Dict[str, Any]]:
    """Generate SEO meta description using AI with comprehensive analysis"""
    if not client:
        st.error("OpenAI client not configured. Please provide API key.")
        return None
    
    try:
        with st.spinner("✨ Crafting perfect meta description..."):
            prompt = f"""
            Create an SEO-optimized meta description for the topic: "{topic}"Requirements:
            - Tone: {tone.lower()}
            - Length: Under {target_length} characters
            - Include relevant keywords naturally
            - Add a compelling call-to-action
            - Make it click-worthy and informative
            
            Return only the meta description text.'''
            
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SEO content writer specializing in meta descriptions that drive clicks and conversions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            description = response.choices[0].message.content.strip()
            
            # Analyze the generated description
            analysis = analyze_meta_description(description, topic)
            
            return {
                'content': description,
                'analysis': analysis
            }
            
    except Exception as e:
        st.error(f"Generation failed: {str(e)}")
        return None

def analyze_meta_description(description: str, topic: str) -> Dict[str, Any]:
    """Analyze meta description for SEO optimization"""
    length = len(description)
    word_count = len(description.split())
    
    # Check for topic keywords
    topic_words = topic.lower().split()
    contains_topic = any(word in description.lower() for word in topic_words)
    
    # Check for action words
    action_words = ['discover', 'learn', 'get', 'find', 'explore', 'boost', 'improve', 'master']
    has_action_word = any(word in description.lower() for word in action_words)
    
    # Generate suggestions
    suggestions = []
    if length > 160:
        suggestions.append("Consider shortening to under 160 characters")
    if length < 120:
        suggestions.append("Consider adding more descriptive content")
    if not contains_topic:
        suggestions.append("Include main topic keywords")
    if not has_action_word:
        suggestions.append("Add action words to encourage clicks")
    if not any(char in description for char in '!?'):
        suggestions.append("Consider adding punctuation for emphasis")
    
    return {
        'length': length,
        'word_count': word_count,
        'contains_topic': contains_topic,
        'has_action_word': has_action_word,
        'suggestions': suggestions,
        'score': calculate_seo_score(length, contains_topic, has_action_word)
    }

def calculate_seo_score(length: int, contains_topic: bool, has_action_word: bool) -> int:
    """Calculate SEO score for meta description"""
    score = 0
    
    # Length score (0-40 points)
    if 120 <= length <= 160:
        score += 40
    elif 100 <= length < 120 or 160 < length <= 180:
        score += 30
    elif 80 <= length < 100 or 180 < length <= 200:
        score += 20
    else:
        score += 10
    
    # Topic relevance (0-30 points)
    if contains_topic:
        score += 30
    
    # Action words (0-30 points)
    if has_action_word:
        score += 30
    
    return min(score, 100)

# ========================
# 📊 MAIN INTERFACE
# ========================
# Sidebar navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    menu = st.radio(
        "Choose Tool", 
        ["🔎 Keyword Explorer", "✍️ Content Generator", "📊 SEO Analytics"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("""
    This tool helps you:
    - Research trending keywords
    - Generate SEO-optimized content
    - Analyze content performance
    """)

# Main content area
if menu == "🔎 Keyword Explorer":
    st.markdown("## 🔎 Keyword Explorer")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        keyword = st.text_input(
            "Enter a niche or seed keyword:",
            placeholder="e.g., 'digital marketing', 'python programming'",
            key="keyword_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        search_button = st.button("🔍 Fetch Trends", type="primary", use_container_width=True)
    
    if search_button:
        if not keyword:
            st.warning("⚠️ Please enter a keyword")
        else:
            trends_data = fetch_keyword_trends(keyword)
            
            if trends_data is not None and not trends_data.empty:
                st.markdown("### 🔥 Top Related Queries")
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Keywords", len(trends_data))
                with col2:
                    avg_volume = trends_data['estimated_volume'].mean()
                    st.metric("Avg. Volume", f"{avg_volume:,.0f}")
                with col3:
                    avg_difficulty = trends_data['difficulty'].mean()
                    st.metric("Avg. Difficulty", f"{avg_difficulty:.0f}%")
                
                # Enhanced dataframe display
                display_df = trends_data.copy()
                display_df['estimated_volume'] = display_df['estimated_volume'].apply(lambda x: f"{x:,}")
                display_df['difficulty'] = display_df['difficulty'].apply(lambda x: f"{x}%")
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "query": "Keyword",
                        "value": "Trend Score",
                        "estimated_volume": "Est. Volume",
                        "difficulty": "Difficulty"
                    }
                )
                
                # Download option
                csv = trends_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"keyword_research_{keyword.replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("🔍 No trending queries found. Try a different keyword or check your internet connection.")

elif menu == "✍️ Content Generator":
    st.markdown("## ✍️ Content Generator")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "Enter your topic:",
            placeholder="e.g., 'benefits of organic SEO', 'machine learning basics'",
            key="topic_input"
        )
    
    with col2:
        tone = st.selectbox(
            "Select tone:",
            ["Professional", "Conversational", "Persuasive", "Informative", "Technical"],
            key="tone_select"
        )
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        target_length = st.slider("Target character length:", 120, 200, 155)
        include_cta = st.checkbox("Include call-to-action", value=True)
    
    if st.button("✨ Generate Meta Description", type="primary", use_container_width=True):
        if not topic:
            st.warning("⚠️ Please enter a topic")
        elif not client:
            st.error("🔑 Please configure OpenAI API key in the sidebar")
        else:
            result = generate_meta_description(topic, tone, target_length)
            
            if result:
                st.markdown("### 📝 Generated Meta Description")
                
                # Display the generated content
                st.markdown(f"""
                <div class="success-box">
                    <h4>Generated Content:</h4>
                    <p style="font-size: 16px; line-height: 1.5;">{result['content']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Analysis metrics
                analysis = result['analysis']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Characters", f"{analysis['length']}/160")
                with col2:
                    st.metric("Words", analysis['word_count'])
                with col3:
                    st.metric("SEO Score", f"{analysis['score']}/100")
                with col4:
                    status = "✅ Good" if analysis['length'] <= 160 else "⚠️ Too Long"
                    st.metric("Length Status", status)
                
                # Detailed analysis
                st.markdown("### 📊 SEO Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**✅ Strengths:**")
                    strengths = []
                    if analysis['contains_topic']:
                        strengths.append("Contains topic keywords")
                    if analysis['has_action_word']:
                        strengths.append("Includes action words")
                    if 120 <= analysis['length'] <= 160:
                        strengths.append("Optimal length")
                    
                    for strength in strengths:
                        st.success(f"• {strength}")
                
                with col2:
                    st.markdown("**💡 Suggestions:**")
                    for suggestion in analysis['suggestions']:
                        st.info(f"• {suggestion}")
                
                # Copy to clipboard (JavaScript)
                st.markdown("### 📋 Copy to Clipboard")
                st.code(result['content'], language=None)

elif menu == "📊 SEO Analytics":
    st.markdown("## 📊 SEO Analytics Dashboard")
    
    st.info("🚧 This feature is coming soon! It will include:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Keyword Analytics:**
        - Search volume trends
        - Competition analysis
        - Ranking opportunities
        - Seasonal patterns
        """)
    
    with col2:
        st.markdown("""
        **Content Performance:**
        - Meta description effectiveness
        - Click-through rates
        - Content optimization scores
        - A/B testing results
        """)
    
    # Mock analytics data
    st.markdown("### 📈 Sample Analytics")
    
    import numpy as np
    
    # Generate sample data
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    search_volume = np.random.randint(1000, 5000, 30)
    ctr = np.random.uniform(2, 8, 30)
    
    analytics_df = pd.DataFrame({
        'Date': dates,
        'Search Volume': search_volume,
        'CTR (%)': ctr.round(2)
    })
    
    st.line_chart(analytics_df.set_index('Date'))

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🚀 AI SEO Specialist Tool | Built with Streamlit & OpenAI</p>
    <p>💡 Tip: Use specific, long-tail keywords for better results</p>
</div>
""", unsafe_allow_html=True)
