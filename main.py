import streamlit as st
from pytrends.request import TrendReq
import openai

# Page config
st.set_page_config(page_title="AI SEO Specialist", layout="centered")
st.title("AI SEO Specialist")
st.write("Boost your SEO with AI-driven keyword research and content generation!")

# Sidebar menu
menu = st.sidebar.radio("Choose Tool", ["Keyword Explorer", "Content Generator"])


#1. KEYWORD EXPLORER TOOL

if menu == "Keyword Explorer":
    keyword = st.text_input("Enter a niche or seed keyword:")

    if st.button("Fetch Trends"):
        pytrends = TrendReq(hl='en-US', tz=330)
        pytrends.build_payload([keyword])

        try:
            trends = pytrends.related_queries()
            related_top = trends[keyword]['top']

            if related_top is not None:
                st.subheader("Related Trending Queries:")
                st.dataframe(related_top)
            else:
                st.warning("No related trending queries found for this keyword.")

        except Exception as e:
            st.error(f"❌ Could not fetch trends. Try a different keyword.\n\n**Error:** {e}")


# 2. CONTENT GENERATOR TOOL

elif menu == "Content Generator":
    topic = st.text_input("Enter a topic for SEO content:")
    tone = st.selectbox("Choose tone:", ["Formal", "Casual", "Neutral"])

    if st.button("Generate Meta Description"):
        try:
            openai.api_key = st.secrets["OPENAI_API_KEY"]

            prompt = f"Write an SEO-friendly meta description about '{topic}' in a {tone} tone."

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert SEO content writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60,
                temperature=0.7
            )

            st.subheader("Generated Meta Description:")
            st.success(response["choices"][0]["message"]["content"].strip())

        except Exception as e:
            st.error(f"Failed to generate content. Check your API key or try again.\n\n**Error:** {e}")


