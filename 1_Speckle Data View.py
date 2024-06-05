from modules.streamlit.components.sidebar import Sidebar
from modules.streamlit.components.st_speckle import Streamlit_Speckle_Components

from modules.speckle.projects import SpeckleProject

import streamlit as st

st.session_state["project_name"] = "Datenansicht Modell"
st.set_page_config(
    page_title=st.session_state["project_name"],
    layout="wide"
)

# Instantiate the main components
sidebar = Sidebar()

# setup sidebar
sidebar.show_options(show_speckle=True, show_chat=False)
commit_url = st.session_state["commit_url"]
project = SpeckleProject(st.session_state["project_name"])

# Instantiate the Speckle Streamlit components
st_speckle = Streamlit_Speckle_Components(project.get_basehandler())

### UI ###

# Header
info = "This page introduces you to the different models in Speckle"
st_speckle.show_header("Datenansicht Modell", info)

# Show the 3D model
st.subheader("Modell Visualisierung")
st_speckle.show_3Dmodel(commit_url)

# Show the data tree
st.subheader("Arbeite mit Modell Informationen")
st_speckle.show_data_tree(project)

# Filter the dataframe
st_speckle.filter_dataframe(show_df=True)
    