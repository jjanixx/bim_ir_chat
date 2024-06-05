import streamlit as st
from pandas import DataFrame
from pandasai import Agent

from modules.speckle.projects import SpeckleProject

from modules.streamlit.messages.chat_output import OutputGenerator
from modules.streamlit.messages.st_chathistory import StreamlitChatHistory
from modules.streamlit.components.st_components import StreamlitComponents

from modules.llm.agent_handler import Pandasai_Agent_Handler


class Streamlit_PandasAI_Components(StreamlitComponents):

    def __init__(self):
        pass

    @st.cache_data(show_spinner=True, hash_funcs={SpeckleProject: lambda x: x.name})
    def choose_data_subset(_self, speckle_project: SpeckleProject, category_name: str):
        """ load the data subset from the speckle project for a given category_name
        
        Args:
            speckle_project (SpeckleProject): the speckle project
            category_name (str): the category name
            
        Returns:
            DataFrame: the pandas dataframe
        """
        
        st.session_state["project_table"] = category_name

        # get basehandler
        basehandler = speckle_project.get_basehandler()
        st.session_state["basehandler"] = basehandler

        # get pandas dataframe
        df = basehandler.get_category_dataframe(st.session_state["project_table"])

        # Show pandas data
        with st.expander("Extracted Data", expanded=False):
            st.write(df)
        
        return df

    def load_chat_history(self, page_title: str):
        """ loads the chat history"""
        # Setup Chat History
        history = StreamlitChatHistory(page_title, "pandasai")

        # display the chat history in Streamlit
        for message in history.history:
            # display in the chat container
            with st.chat_message(message["role"]):
                # generate placeholder for message
                message_placeholder = st.empty()
                # get the correct Output class
                output = OutputGenerator.get_output(message["content"])
                # load the chat message
                output.load_chat_message(message["content"], message_placeholder)
        
        return history

    def new_user_query(self, df: DataFrame, agent: Agent, history: StreamlitChatHistory):
        """ handle a new user query, sends to API and returns the response, updates the chat history"""
        if prompt := st.chat_input("Frag mich alles über deine BIM Daten..."):
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                # generate placeholder for message
                message_placeholder = st.empty()

                # get assistant response via API
                assistant_response = agent.chat(prompt)

                # generate output message in Streamlit
                output = OutputGenerator.get_output(assistant_response)
                output.return_chat_message(assistant_response, message_placeholder)
                
                # Show executed code in Streamlit
                with st.expander("Understand Query"):
                    self._understand_message(agent)
            
            # for successful chat, add to history
            # Add user message to chat history
            history.append({"role": "user", "content": prompt, "type": "string"})
            # st.session_state.messages.append({"role": "user", "content": prompt, "type": "string"})
            # Add assistant message to chat history
            history.append(output.save_chat_message(assistant_response))
            # st.session_state["messages"].append(output.save_chat_message(assistant_response)) 

        return history

    def _understand_message(self, agent: Agent):
        """ show the executed code in the chat"""

        # create three tabs
        tab1, tab2, tab3 = st.tabs(["Code", "Explanation", "Full Log"])

        # Code
        with tab1:
            st.code(Pandasai_Agent_Handler.load_code(agent))

        # Explain
        with tab2:
            st.write(agent.explain())

        # Show Logs
        with tab3:
            st.write(Pandasai_Agent_Handler.return_verbose(agent))