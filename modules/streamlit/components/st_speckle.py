from modules.speckle.data_handler.base_handler import BaseHandler
from modules.speckle.projects import SpeckleProject
from modules.streamlit.components.st_components import StreamlitComponents

import streamlit as st
import streamlit.components.v1 as components
from pandas import DataFrame
import json

class Streamlit_Speckle_Components(StreamlitComponents):

    """ This class contains all the streamlit components for the Speckle page.
    extra class is important for the caching of the data"""

    def __init__(self, basehandler: BaseHandler) -> None:
        self.basehandler = basehandler

    def show_3Dmodel(self, commit_url: str):
        return components.iframe(commit_url, height=600)
    
    @st.cache_data(show_spinner=True, hash_funcs={SpeckleProject: lambda x: x.name})
    def load_json_from_project(_self, project: SpeckleProject):
        return project.load_json()

    def show_data_tree(self, project: SpeckleProject):
        """ Streamlit module to show the data tree of the Speckle project
        
        Args:
            project (SpeckleProject): the project to show the data tree
        """
        with st.expander("Visualisiere die Daten in einer Baumstruktur", expanded=True):
            base_dict = self.load_json_from_project(project)
            st.json(base_dict, expanded=False)

            if st.button("Generiere eine Download Datei"):
                base_json = json.dumps(base_dict)
                st.download_button(
                    "Download JSON 🔽",
                    base_json,
                    f"{'RevitData'}.json",
                    mime="application/json",
                )
    
    def choose_category(self):
        """ Streamlit module to choose the category of the Speckle project"""
        # Select Box to choose the category
        selected_category = st.selectbox("Wähle eine Kategorie aus", self.basehandler.categories)
        return selected_category
    
    def filter_dataframe(self, show_df: bool = False):
        """ Steamlit module to filter the dataframe from the Speckle project"""

        # Get the selected category
        st.subheader("Filter deine Daten")
        # Select Box to choose the category
        selected_category = self.choose_category()
        
        # bekomme alle Category Elements -> TODO: Was sind Category Elements?
        category_elements = self.basehandler.base[selected_category]
        # Lade die dazugehörigen Parameter
        parameters = self.get_parameters_from_category(self.basehandler, selected_category)

        # Choose all parameters for the table
        with st.expander("Wähle relevante Parameter zu " + selected_category + " aus.", expanded=True):
            # Überschriften
            selected_title = 'Ausgewählte Parameter'
            colum_title = "Deine Revit Parameter der Kategorie " + selected_category + ":"
            
            # Erstelle das dataframe
            df_param = DataFrame(parameters, columns=[colum_title])
            df_param[selected_title] = True
            # Erstelle den Data Editor
            selected_df_param = st.data_editor(df_param, width=None, height=None, use_container_width=True, hide_index=True,
                                            column_order=(selected_title, colum_title))
            # Erstelle die Liste der ausgewählten Parameter
            selected_parameters = selected_df_param[selected_df_param[selected_title]][colum_title].tolist()

            if selected_parameters:
                # create the dataframe
                result_DF = self.create_dataframe(self.basehandler, category_elements, selected_parameters)
                # if selected show the dataframe on streamlit
                if show_df:
                    # filter the dataframe
                    result_DF = self.filter_pandas_dataframe(result_DF)
                    # load the dataframe
                    st.data_editor(result_DF)
                    # Download button for the resulting dataframe
                    st.download_button(
                        "Download CSV 🔽",
                        result_DF.to_csv().encode("utf-8"),
                        f"{'RevitData'}.csv",
                        mime="text/csv",
                    )
                    # potentially add remark that we only show the first 15 columns
                    if self.add_text:
                        st.markdown(self.add_text)
        return result_DF

    @st.cache_data(hash_funcs={BaseHandler: lambda x: hash(str(x.base.id))})
    def get_parameters_from_category(_self, basehandler: BaseHandler, selected_category: str):
        return basehandler.get_ASparameters_from_category(selected_category)

    @st.cache_data(hash_funcs={BaseHandler: lambda x: hash(str(x.base.id))})
    def create_dataframe(_self, basehandler: BaseHandler, _selected_category: str, selected_parameters: list[str]):
        return basehandler._create_dataframe_from_elements(_selected_category, selected_parameters)
    
    def show_speckle_api_key_missing(self):
        """
        Displays a message if the user has not entered an API key
        """
        st.markdown(
            """
            <div style='text-align: center;'>
                <h4>Enter your <a href="https://speckle.xyz/user/settings" target="_blank">Speckle API key</a> to start load porjects</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def filter_pandas_dataframe(self, df: DataFrame):
        """
        Filter the dataframe for better output
        """
        # remove columns with int64
        df = df.select_dtypes(exclude=['int64'])
        # remove empty columns
        df = df.dropna(axis=1, how='all')
        # show maximum 15 columns
        if len(df.columns) > 15:
            df = df[df.columns[:15]]
        self.add_text = "Remark: Too many columns to display. Only the first 15 columns are shown."
        return df