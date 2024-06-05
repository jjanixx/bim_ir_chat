from modules.streamlit.components.sidebar import Sidebar
from modules.streamlit.components.st_pandasai import Streamlit_PandasAI_Components

from modules.speckle.projects import SpeckleProject

from modules.llm.agent_handler.pandasai_agent import Pandasai_Agent_Handler

import streamlit as st

# Set the page title
page_title = "PandasAI Prototype"
st.session_state["project_name"] = page_title
st.set_page_config(
    page_title=page_title,
    layout="wide"
)

# Set the page title in the session state
st.session_state["page_title"] = page_title

# Instantiate the main components
sidebar = Sidebar()
st_chat = Streamlit_PandasAI_Components()

# Show the Header
info = """This is a prototype for the PandasAI agent. 
It uses the PandasAI agent to chat with the user.
You can choose your category and start chatting with the data."""
st_chat.show_header("PandasAI Prototype", info=info)

# Load the LLMSettings, remark: Bug here
sidebar.show_options(show_speckle=True, show_chat=True)
llmsettings = sidebar.llmsettings

# get project data
speckle_project = SpeckleProject(st.session_state.get("project_name"))

#streamlit selectbox to choose the correct table
category_name = st.selectbox("Choose a table", speckle_project.get_categories())

# get the data subset and display it
df = st_chat.choose_data_subset(speckle_project, category_name)

# Setup agent
agent = Pandasai_Agent_Handler.setup_agent(df, llmsettings)

# Load Chat History
history = st_chat.load_chat_history(page_title)

# New Chat
history = st_chat.new_user_query(df, agent, history)