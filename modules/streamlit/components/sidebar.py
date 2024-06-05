import streamlit as st

from modules.speckle.projects import ProjectsOverview
from modules.llm.llm_settings import LLMSettings

class Sidebar:

    MODEL_OPTIONS = LLMSettings.MODEL_OPTIONS
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

    def __init__(self):
        self.llmsettings = LLMSettings()

    def show_speckle_projects(self):
        """
        gives overview of all speckle projects and lets user select one
        saves the selected project in session state
        """
        speckle_projects = ProjectsOverview()
        project_name = st.selectbox('Project URLs',
            options=list(speckle_projects.projects.keys()), label_visibility='collapsed', placeholder='Select a project')
        st.session_state["project_name"] = project_name
        st.session_state["commit_url"] = speckle_projects.projects[project_name]

    @staticmethod
    def reset_chat_button():
        if st.button("Reset chat"):
            st.session_state["reset_chat"] = True

    def model_selector(self):
        model = st.selectbox(label="Model", options=self.MODEL_OPTIONS)
        st.session_state["model"] = model
        self.llmsettings.model = model

    def temperature_slider(self, settings: LLMSettings = None):
        temperature = st.slider(
            label="Temperature",
            min_value=self.TEMPERATURE_MIN_VALUE,
            max_value=self.TEMPERATURE_MAX_VALUE,
            value=self.TEMPERATURE_DEFAULT_VALUE,
            step=self.TEMPERATURE_STEP,
        )
        self.llmsettings.temperature = temperature
        st.session_state["temperature"] = temperature
        
    def show_options(self, show_speckle= False, show_chat= False):
        """
        calls the different sidebar modules
        """

        if show_speckle:
            with st.sidebar.expander("🛠️ Wähle Bauprojekt", expanded=True):
                self.show_speckle_projects()

        if show_chat:

            with st.sidebar.expander("🛠️ Konfiguriere Model", expanded=False):
                self.reset_chat_button()
                self.model_selector()
                self.temperature_slider()
                st.session_state.setdefault("model", self.MODEL_OPTIONS[0])
                st.session_state.setdefault("temperature", self.TEMPERATURE_DEFAULT_VALUE)

    