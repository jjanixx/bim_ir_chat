from modules.llm.agent_handler import Langchain_Agent_Handler
from modules.streamlit.components import Streamlit_Langchain_Components
from modules.streamlit.components.sidebar import Sidebar
from modules.speckle.projects import SpeckleProject

import streamlit as st

# Set the page title
page_title = "Langchain Chat"
st.session_state["project_name"] = page_title
st.set_page_config(
    page_title=page_title,
    layout="wide"
)

# Instantiate the main components
sidebar = Sidebar()
st_chat = Streamlit_Langchain_Components()

# Show the Header
info = """This is a prototype for the Langchain agent."""
st_chat.show_header(page_title, info=info)

# Load the LLMSettings
sidebar.show_options(show_speckle=True, show_chat=True)
llmsettings = sidebar.llmsettings

# get project data
speckle_project = SpeckleProject(st.session_state.get("project_name"))

# Setup agent
# Streamlit actually reruns the setup every time the user interacts with the page
agent = Langchain_Agent_Handler.setup_agent(llmsettings)

# Load Chat History
history = st_chat.load_chat_history(page_title)

# New Chat
history = st_chat.new_user_query(agent, history)