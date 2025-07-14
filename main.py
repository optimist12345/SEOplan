def fetch_keyword_trends(keyword: str):
    """Fetch related queries from Google Trends"""
    try:
        with st.spinner("Analyzing search trends..."):
            pytrends = TrendReq(hl='en-US', tz=330)
            
            # Build payload with timeout and better error handling
            pytrends.build_payload(
                kw_list=[keyword],
                timeframe='today 12-m',
                geo='',
                gprop=''
            )
            
            # Get related queries with additional checks
            trends = pytrends.related_queries()
            
            # Safely access the nested dictionary
            if not trends or keyword not in trends:
                return None
                
            related_data = trends[keyword]
            
            # Check if 'top' exists and has data
            if not related_data or 'top' not in related_data:
                return None
                
            top_queries = related_data['top']
            
            return top_queries if not top_queries.empty else None
            
    except Exception as e:
        st.error(f"Trends API error: {str(e)}")
        return None

# In your main Keyword Explorer section:
if menu == "Keyword Explorer":
    st.header(" Keyword Explorer")
    keyword = st.text_input(
        "Enter a niche or seed keyword:",
        placeholder="e.g., 'digital marketing'",
        key="keyword_input"
    )
    
    if st.button("Fetch Trends", type="primary"):
        if not keyword.strip():
            st.warning("Please enter a valid keyword")
        else:
            trends_data = fetch_keyword_trends(keyword.strip())
            
            if trends_data is not None:
                st.subheader("🔥 Top Related Queries")
                st.dataframe(
                    trends_data.head(20),  # Show top 20 results
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "query": "Related Query",
                        "value": st.column_config.NumberColumn(
                            "Popularity",
                            format="%d%%",
                            help="Relative popularity score"
                        )
                    }
                )
            else:
                st.info("No trending data available for this keyword. Try a more popular or different keyword.")
                st.markdown("""
                **Tips:**
                - Use broader terms (e.g., "marketing" instead of "viral marketing tactics")
                - Check spelling
                - Try English-language keywords
                - Avoid very recent trends/new terms
                """)
