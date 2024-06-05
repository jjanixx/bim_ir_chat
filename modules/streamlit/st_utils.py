import os
import pandas as pd
import streamlit as st
import pdfplumber
from dotenv import load_dotenv

from modules.llm.chatbots import SinglePDFChatbot, BIMIRChatBot
from modules.llm.embedder import DocsEmbbeder
from modules.llm.llm_settings import LLMSettings
from modules.speckle.projects import SpeckleProject

load_dotenv()

class Utilities:

    @staticmethod
    def load_openai_api_key():
        """
        Loads the OpenAI API key from the .env file or 
        from the user's input and returns it
        """
        if not hasattr(st.session_state, "api_key"):
            st.session_state.api_key = None
        #you can define your API key in .env directly
        if os.path.exists(".env") and os.environ.get("OPENAI_API_KEY") is not None:
            user_api_key = os.environ["OPENAI_API_KEY"]
            st.sidebar.success("API key loaded from .env", icon="🚀")
        elif st.secrets["OPENAI_API_KEY"] is not None:
            user_api_key = st.secrets["OPENAI_API_KEY"]
            st.sidebar.success("API key loaded from secrets", icon="🚀")
        else:
            if st.session_state.api_key is not None:
                user_api_key = st.session_state.api_key
                st.sidebar.success("API key loaded from previous input", icon="🚀")
            else:
                user_api_key = st.sidebar.text_input(
                    label="#### Your OpenAI API key 👇", placeholder="sk-...", type="password"
                )
        if user_api_key:
            st.session_state.api_key = user_api_key

        return user_api_key
    
    def load_llm_api_key(self, llmsettings: LLMSettings):
        """
        Loads the OpenAI API key from the .env file or 
        from the user's input and returns it
        """
        model = llmsettings.model

        if not hasattr(st.session_state, "api_key"):
            st.session_state.api_key = None
        #you can define your API key in .env directly
        if os.path.exists(".env") and os.environ.get("OPENAI_API_KEY") is not None:
            user_api_key = llmsettings.get_correct_api_key()
            st.sidebar.success("API key loaded from .env", icon="🚀")
        elif st.secrets["OPENAI_API_KEY"] is not None:
            user_api_key = st.secrets["OPENAI_API_KEY"]
            st.sidebar.success("API key loaded from secrets", icon="🚀")
        else:
            if st.session_state.api_key is not None:
                user_api_key = st.session_state.api_key
                st.sidebar.success("API key loaded from previous input", icon="🚀")
            else:
                user_api_key = st.sidebar.text_input(
                    label="#### Your LLM API key 👇", placeholder="sk-...", type="password"
                )
        if user_api_key:
            st.session_state.api_key = user_api_key

        return user_api_key
    
    def load_speckle_api_key():
        """
        Loads the Speckle auth token from the .env file or
        from the user's input and returns it
        """

        # create empty session state if not existing
        if not hasattr(st.session_state, "auth_token"):
            st.session_state.auth_token = None
        
        # you can define your API key in .env directly
        if os.path.exists(".env") and os.environ.get("SPECKLE_AUTH_TOKEN") is not None:
            st.session_state.auth_token = os.environ.get("SPECKLE_AUTH_TOKEN")
            # st.sidebar.success("Speckle API key loaded from .env", icon="🚀")
        else:
            # if the session state already contains an api key, use it
            if st.session_state.auth_token is not None:
                speckle_api_key = st.session_state.auth_token
                # st.sidebar.success("API key loaded from previous input", icon="🚀")
            # otherwise ask for it
            else:
                speckle_api_key = st.sidebar.text_input(
                    label="#### Your Speckle API key 👇", placeholder="sk-...", type="password"
                )
                if speckle_api_key:
                    st.session_state.auth_token = speckle_api_key
        
        return st.session_state.auth_token
    
    @staticmethod
    def handle_upload(file_types):
        """
        Handles and display uploaded_file
        :param file_types: List of accepted file types, e.g., ["csv", "pdf", "txt"]
        """
        uploaded_file = st.sidebar.file_uploader("upload", type=file_types, label_visibility="collapsed")
        if uploaded_file is not None:

            def show_csv_file(uploaded_file):
                file_container = st.expander("Your CSV file :")
                uploaded_file.seek(0)
                shows = pd.read_csv(uploaded_file)
                file_container.write(shows)

            def show_pdf_file(uploaded_file):
                file_container = st.expander("Dein PDF :")
                with pdfplumber.open(uploaded_file) as pdf:
                    pdf_text = ""
                    for page in pdf.pages:
                        pdf_text += page.extract_text() + "\n\n"
                file_container.write(pdf_text)
            
            def show_txt_file(uploaded_file):
                file_container = st.expander("Your TXT file:")
                uploaded_file.seek(0)
                content = uploaded_file.read().decode("utf-8")
                file_container.write(content)
            
            def get_file_extension(uploaded_file):
                return os.path.splitext(uploaded_file)[1].lower()
            
            file_extension = get_file_extension(uploaded_file.name)

            # Show the contents of the file based on its extension
            #if file_extension == ".csv" :
            #    show_csv_file(uploaded_file)
            if file_extension== ".pdf" : 
                show_pdf_file(uploaded_file)
            elif file_extension== ".txt" : 
                show_txt_file(uploaded_file)

        else:
            st.session_state["reset_chat"] = True

        #print(uploaded_file)
        return uploaded_file

    @staticmethod
    def setup_docs_chatbot(uploaded_file, model, temperature):
        """
        Sets up the chatbot with the uploaded file, model, and temperature
        """
        embeds = DocsEmbbeder()

        with st.spinner("Processing..."):
            uploaded_file.seek(0)
            file = uploaded_file.read()
            # Get the document embeddings for the uploaded file
            vectors = embeds.getEmbeds(file, uploaded_file.name)

            # Create a Chatbot instance with the specified model and temperature
            chatbot = SinglePDFChatbot(model, temperature, vectors)
        st.session_state["ready"] = True

        return chatbot
    
    @staticmethod
    def setup_3D_chatbot(project: SpeckleProject, llmsettings: LLMSettings):
        """
        Sets up the chatbot with the uploaded file, model, and temperature
        """

        with st.spinner("Processing..."):

            # Create a Chatbot instance with the specified model and temperature
            chatbot = BIMIRChatBot(project, llmsettings)
        st.session_state["ready"] = True

        return chatbot


    
