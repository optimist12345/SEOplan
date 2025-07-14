import streamlit as st
from pytrends.request import TrendReq
import openai

st.set_page_config(page_title="AI SEO Specialist", layout="centered")
st.title("🚀 AI SEO Specialist")
st.write("Boost your SEO with AI-driven keyword research and content generation!")

menu = st.sidebar.radio("Choose Tool", ["Keyword Explorer", "Content Generator"])

if menu == "Keyword Explorer":
    keyword = st.text_input("Enter a niche or seed keyword:")
    if st.button("Fetch Trends"):
        pytrends = TrendReq(hl='en-US', tz=330)
        pytrends.build_payload([keyword])
        trends = pytrends.related_queries()
        if trends and keyword in trends:
            st.subheader("Related Trending Queries:")
            st.dataframe(trends[keyword]['top'])
        else:
            st.warning("No trends found. Try another keyword.")

elif menu == "Content Generator":
    topic = st.text_input("Enter topic for SEO content:")
    tone = st.selectbox("Choose Tone:", ["Formal", "Casual", "Neutral"])
    if st.button("Generate Meta Description"):
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        prompt = f"Write an SEO-friendly meta description about '{topic}' in a {tone} tone."
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=60
        )
        st.subheader("Generated Meta Description:")
        st.success(response["choices"][0]["text"].strip())

