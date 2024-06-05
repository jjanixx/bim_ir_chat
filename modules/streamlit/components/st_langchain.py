from .st_components import StreamlitComponents

from modules.streamlit.messages import StreamlitChatHistory, OutputGenerator
from modules.llm.agent_handler import Langchain_Agent_Handler

import streamlit as st
from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from langchain.callbacks.tracers import LangChainTracer

class Streamlit_Langchain_Components(StreamlitComponents):

    def __init__(self):
        super().__init__()

    def load_chat_history(self, page_title: str) -> StreamlitChatHistory:
        """ loads the chat history from the list of Human and AI messages
        converts the Langchain messages to Streamlit chat outputs"""
        # Setup Chat History
        chat_history = StreamlitChatHistory(page_title, "langchain")

        # get the right role depending on the Langchain message
        for message in chat_history.history:
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            else:
                raise ValueError("Invalid message type")
            content = message.content

            # display in the chat container
            with st.chat_message(role):
                # generate placeholder for message
                message_placeholder = st.empty()
                # get the correct Output class
                output = OutputGenerator.get_output(content)
                # load the chat message
                output.load_chat_message(content, message_placeholder)
        
        return chat_history
    
    def new_user_query(self, agent: AgentExecutor, chat_history: StreamlitChatHistory) -> StreamlitChatHistory:
        """ handle a new user query, sends to API and returns the response, updates the chat history"""
        if prompt := st.chat_input("Frag mich alles über deine BIM Daten..."):
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                # generate placeholder for message
                message_placeholder = st.empty()

                # load Langchain Tracer (for LangSmith)
                tracer = LangChainTracer()
                # get assistant response via API
                assistant_response = agent.invoke(
                    {
                        "input": prompt,
                        "chat_history": chat_history.history
                    },
                    config={"callbacks": [tracer]}
                )
                response_output = assistant_response["output"]

                # generate output message in Streamlit
                output = OutputGenerator.get_output(response_output)
                output.return_chat_message(response_output, message_placeholder)

                # Show intermediate steps in Streamlit
                with st.expander("Zwischenschritte des Agenten anzeigen"):
                    # st.write(Langchain_Agent_Handler.show_intermediate_steps(assistant_response))
                    self._understand_message(assistant_response)
            
            # for successful chat, Add user message to chat history
            chat_history.append(HumanMessage(prompt))
            # Add assistant message to chat history
            chat_history.append(AIMessage(response_output))

        return chat_history
    
    def test_tool(self, agent: AgentExecutor, chat_history: StreamlitChatHistory) -> StreamlitChatHistory:
        """ handle a new user query, sends to API and returns the response, updates the chat history"""
        if prompt := st.chat_input("Frag mich alles über deine BIM Daten..."):
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                # generate placeholder for message
                message_placeholder = st.empty()

                # load Langchain Tracer (for LangSmith)
                tracer = LangChainTracer()
                # get assistant response via API
                assistant_response = agent.invoke(
                    {
                        "question": prompt,
                        "chat_history": chat_history.history
                    },
                    config={"callbacks": [tracer]}
                )
                response_output = assistant_response["output"]

                # generate output message in Streamlit
                output = OutputGenerator.get_output(response_output)
                output.return_chat_message(response_output, message_placeholder)

                # Show intermediate steps in Streamlit
                with st.expander("Zwischenschritte des Agenten anzeigen"):
                    # st.write(Langchain_Agent_Handler.show_intermediate_steps(assistant_response))
                    self._understand_message(assistant_response)
            
            # for successful chat, Add user message to chat history
            chat_history.append(HumanMessage(prompt))
            # Add assistant message to chat history
            chat_history.append(AIMessage(response_output))

        return chat_history
    

    def _understand_message(self, assistant_response: dict):
        """ show the executed code in the chat"""

        # create three tabs
        tab1, tab2, tab3 = st.tabs(["Code", "Explanation", "Full Log"])

        # Code
        with tab1:
            st.write(Langchain_Agent_Handler.recursive_intermediate_parser(assistant_response))

        # Explain
        with tab2:
            st.write(assistant_response["intermediate_steps"])

        # Show Logs
        with tab3:
            st.write(assistant_response)