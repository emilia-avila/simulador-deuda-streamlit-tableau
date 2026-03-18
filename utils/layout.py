import streamlit as st

def firma_sidebar():

    st.sidebar.markdown(
        """
        <div style="font-size: 12px; color: #9CA3AF;">
            Elaborado por: Emilia Ávila | Data Analytics
        </div>
        <a href="https://www.linkedin.com/in/emilia-avila-vasconez" target="_blank">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" 
                 width="16" style="margin-top: 4px;">
        </a>
        """,
        unsafe_allow_html=True
    )