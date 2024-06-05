import streamlit as st

class StreamlitComponents:
    
    def __init__(self):
        pass

    def show_header(self, heading, info= None):
        """
        Displays the header of the app
        """
        st.markdown(
            f"""
            <h1 style='text-align: left;'> {heading} </h1>
            """,
            unsafe_allow_html=True,
        )

        if info:
            st.expander("ℹ️ Info about this Page", expanded=False).markdown(info)