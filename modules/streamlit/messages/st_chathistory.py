import streamlit as st

from langchain_core.messages import AIMessage, HumanMessage

class StreamlitChatHistory:

    """save the chat history in the Streamlit session state
    
    idea: perform action, then reload session states which safe the messages for all pages
    
    Variables:
    chat_name (str): the name of the chat
    history (list): the chat history for this specific page
    chat_state (str): the chat state for this specific page
    """

    def __init__(self, chat_name, framework):
        """ initialize the chat history in the Streamlit session state 
        
        Args:
            chat_name (str): the name of the chat
        """
        # initialize an empty chat history
        self.chat_name = chat_name

        # initialize the framework
        assert framework in ["langchain", "pandasai"], "Invalid framework"
        self.framework = framework

        # load the correct history and chat state
        self._load_correct_history()
        self._load_correct_chat_state()

        # initialize the session states with dict, if not existing
        if "history" not in st.session_state:
            st.session_state["history"] = {chat_name: []}
        if "chat_state" not in st.session_state:
            st.session_state["chat_state"] = {chat_name: "assistant"}

        # check for reset
        if st.session_state.get("reset_chat", True):
            self.reset()

    def _load_correct_history(self):
        """load the correct chat history for this page from the Streamlit session state"""
        overall_history = st.session_state.get("history", {})
        if self.chat_name not in overall_history:
            self.history = []
        else:
            self.history = overall_history[self.chat_name]

    def _load_correct_chat_state(self):
        """load the correct chat state for this page from the Streamlit session state"""
        overall_chat_state = st.session_state.get("chat_state", {})
        if self.chat_name not in overall_chat_state:
            self.chat_state = "assistant"
        else:
            self.chat_state = overall_chat_state[self.chat_name]

    def reload_st_states(self):
        """central function: reload the chat history in the Streamlit session state"""
        # update the history state
        overall_history = st.session_state.history
        overall_history[self.chat_name] = self.history
        st.session_state.history = overall_history
        # check and update chat state
        # self.check_valid_state()
        st.session_state.chat_state[self.chat_name] = self.chat_state

    def check_valid_state(self):
        """check if the chat state is valid"""
        # check for valid inputs
        assert self.chat_state in ["user", "assistant"], f"Invalid chat state: {self.chat_state}"

    def check_valid_history_format(self, new_message):
        """check if the new message is in the correct format for the chat history
        
        Args:
            new_message (dict): the new message
        """
        if self.framework == "pandasai":
            # check correct type
            assert isinstance(new_message, dict), "Message is not a dictionary"

            # check for correct keys
            assert "role" in new_message, "Role is missing in message"
            assert "content" in new_message, "Content is missing in message"
            assert "type" in new_message, "Type is missing in message"

            # check values
            assert new_message["role"] in ["user", "assistant"], "Invalid role in message"
            # assert type(new_message["content"]) in OutputGenerator.possible_outputs(), f"Invalid content in message, type is {type(new_message['content'])}"
        else:
            # message is a HumanMessage or AIMessage
            assert isinstance(new_message, HumanMessage) or isinstance(new_message, AIMessage), "Message is not a HumanMessage or AIMessage"

    def reset(self):
        """reset the chat history in the Streamlit session state"""
        # initialize the history file
        self.history = []
        # reset the chat state
        self.chat_state = "assistent"
        # reassign the session states
        self.reload_st_states()
        # reset the session state for the button
        st.session_state["reset_chat"] = False

    def append(self, message):
        """ append a message to the chat history list
        
        Args:
            message (dict): the new message
        """
        # check the format
        self.check_valid_history_format(message)
        # append message
        self.history.append(message)
        # reassign the session states
        self.reload_st_states()