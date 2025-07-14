import streamlit as st
from pytrends.request import TrendReq
from openai import OpenAI  # Updated import
import os


# CONFIGURATION

def configure_openai():
    """Initialize OpenAI client with multiple fallback options"""
    try:
        # Try Streamlit secrets first
        if "OPENAI_API_KEY" in st.secrets:
            return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Fallback to environment variable
        if os.getenv("OPENAI_API_KEY"):
            return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Final fallback to user input
        with st.sidebar:
            st.warning("API key not found in secrets")
            temp_key = st.text_input("Enter OpenAI API Key:", type="password")
            if temp_key:
                return OpenAI(api_key=temp_key)
        
        st.error("API key required to continue")
        st.stop()
    except Exception as e:
        st.error(f"API configuration failed: {str(e)}")
        st.stop()

# ========================
# 🖥️ PAGE SETUP
# ========================
st.set_page_config(
    page_title="AI SEO Specialist",
    page_icon="*_*",
    layout="centered"
)

st.title(" AI SEO Specialist")
st.caption("Boost your SEO with AI-driven keyword research and content generation!")

# Initialize OpenAI client
client = configure_openai()

# ========================
# TOOL FUNCTIONS
# ========================
def fetch_keyword_trends(keyword: str):
    """Fetch related queries from Google Trends"""
    try:
        with st.spinner("Analyzing search trends..."):
            pytrends = TrendReq(hl='en-US', tz=330)
            pytrends.build_payload([keyword])
            trends = pytrends.related_queries()
            return trends[keyword]['top']
    except Exception as e:
        st.error(f"Trends API error: {str(e)}")
        return None

def generate_meta_description(topic: str, tone: str) -> str:
    """Generate SEO meta description using AI"""
    try:
        with st.spinner("✨ Crafting perfect meta description..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SEO content writer. Create compelling meta descriptions under 160 characters."
                    },
                    {
                        "role": "user",
                        "content": f"Write an SEO-friendly meta description about '{topic}' in a {tone.lower()} tone."
                    }
                ],
                max_tokens=60,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Generation failed: {str(e)}")
        return None


#MAIN INTERFACE

with st.sidebar:
    st.header("Navigation")
    menu = st.radio("Choose Tool", ["Keyword Explorer", "Content Generator"])

#  Keyword Explorer Tool
if menu == "Keyword Explorer":
    st.header("🔎 Keyword Explorer")
    keyword = st.text_input(
        "Enter a niche or seed keyword:",
        placeholder="e.g., 'digital marketing'",
        key="keyword_input"
    )
    
    if st.button("Fetch Trends", type="primary"):
        if not keyword:
            st.warning("Please enter a keyword")
        else:
            trends_data = fetch_keyword_trends(keyword)
            if trends_data is not None:
                if not trends_data.empty:
                    st.subheader("Top Related Queries")
                    st.dataframe(
                        trends_data,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No trending queries found. Try a different keyword.")

#  Content Generator Tool
elif menu == "Content Generator":
    st.header(" Content Generator")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        topic = st.text_input(
            "Enter your topic:",
            placeholder="e.g., 'benefits of organic SEO'",
            key="topic_input"
        )
    
    with col2:
        tone = st.selectbox(
            "Tone:",
            ["Professional", "Conversational", "Persuasive", "Informative"],
            key="tone_select"
        )
    
    if st.button("Generate Meta Description", type="primary"):
        if not topic:
            st.warning("Please enter a topic")
        else:
            description = generate_meta_description(topic, tone)
            if description:
                st.subheader(" Generated Meta Description")
                st.success(description)
                st.caption(f"Character count: {len(description)}/160")
