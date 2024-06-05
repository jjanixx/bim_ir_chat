from pandas import DataFrame
from pandasai import SmartDataframe, Agent
from numpy import int64

from modules.llm.agent_handler.pandasai_agent import Pandasai_Agent_Handler

import streamlit as st
from io import StringIO
import os
import time

from abc import ABC

class OutputGenerator(ABC):
    
    """ factory Design Pattern to generate the correct output class for the message type """

    @staticmethod
    def get_output(message):
        """ Returns the correct output class for the message type"""
        # check for correct type
        # assert type(message) in OutputGenerator.possible_outputs(), "Invalid message type"
        
        # Return the correct output class
        if type(message) == DataFrame:
            return OutputDataFrame()
        elif type(message) == int64:
            return OutputInteger()
        elif type(message) == str and message.endswith(".png"):
            return OutputImage()
        elif type(message) == str:
            return OutputString()
        else:
            return Output()
        
    @staticmethod
    def possible_outputs():
        """ Returns the possible output classes"""
        return [str, int64, DataFrame]


class Output(ABC):

    """ Abstract class for the output classes """

    def __init__(self):
        self.message_type = None
    
    def return_chat_message(self, message, message_placeholder):
        """
        Returns a chat message
        """
        message_placeholder.markdown(message)

    def save_chat_message(self, message):
        """
        Saves a chat message
        """
        return {"role": "assistant", "content": message, "type": self.message_type}
    
    def load_chat_message(self, message, message_placeholder):
        """
        Loads a chat message
        """
        return self.return_chat_message(message, message_placeholder)
    
    def _get_message_number(self, message):
        """ Returns the number of the message on this page, needed for specifying file names"""
        # get current page
        current_page = st.session_state.get("project_name")
        # get the history
        if st.session_state.history:
            overall_history = st.session_state.history
            if current_page in overall_history:
                history = st.session_state.history[current_page]
                return len(history)
            else:
                return 0
        else:
            return TypeError("No history found")


class OutputDataFrame(Output):

    def __init__(self):
        super().__init__()
        self.message_type = "DataFrame"
        self.add_text = None
    
    def return_chat_message(self, message, message_placeholder):
        """
        Returns a pandas table
        """
        # Filter the dataframe
        message = self.filter_dataframe(message)
        
        # Output the dataframe
        message_placeholder.dataframe(message)

        # Check for additional text
        if self.add_text:
            st.markdown(self.add_text)

        # # Get Message Number
        # page_title = st.session_state.get("project_name")
        # number_message = self._get_message_number(message)

        # # Create Download Button
        # st.download_button(
        #     label="📥 Download CSV",
        #     data=self.convert_df_to_csv(message),
        #     file_name=f"dataframe_{page_title}_{number_message}.csv",
        #     mime="text/csv",
        #     key=f'download_answer_{page_title}_{number_message}'
        # )
        
    def save_chat_message(self, message):
        return {"role": "assistant", "content": message, "type": self.message_type}
    
    def filter_dataframe(self, df: DataFrame):
        """
        Filter the dataframe for better output
        """
        # remove empty columns
        df = df.dropna(axis=1, how='all')
        # show maximum 15 columns
        if len(df.columns) > 15:
            # Create string with name of unused columns
            unused_columns = ", ".join(df.columns[15:])

            # get filtered dataframe
            df = df[df.columns[:15]]

            self.add_text = f"Remark: Too many columns to display. Only the first 15 columns are shown.\nFollowing columns are not displayed: {unused_columns}"
        return df
    
    def convert_df_to_csv(self, df):
        output = StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return output.getvalue()
        

class OutputString(Output):

    def __init__(self):
        super().__init__()
        self.message_type = "String"

    def return_chat_message(self, message, message_placeholder):
        """
        Returns a string
        """
        full_response = ""
        # Simulate stream of response with milliseconds delay
        for chunk in message.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(message)

    def load_chat_message(self, message, message_placeholder):
        return message_placeholder.markdown(message)


class OutputImage(Output):

    def __init__(self):
        super().__init__()
        self.message_type = "Image"

    def return_chat_message(self, message, message_placeholder):
        """
        Returns an image
        """
        # get message number
        message_number = self._get_message_number(message)

        # message_placeholder.image(message)
        self.export_dir = f'exports/charts/temp_chart_{message_number}.png'
        os.rename(message, self.export_dir)
        message_placeholder.image(self.export_dir)

    def save_chat_message(self, message):
        # return {"role": "assistant", "content": self.export_dir, "type": self.message_type}
        return {"role": "assistant", "content": self.export_dir, "type": self.message_type}
    
    def load_chat_message(self, message, message_placeholder):
        return message_placeholder.image(message)
    

class OutputInteger(Output):

    def __init__(self):
        super().__init__()
        self.message_type = "Integer"

    def return_chat_message(self, message, message_placeholder):
        """
        Returns an integer
        """
        message_placeholder.markdown(message)

    def save_chat_message(self, message):
        return {"role": "assistant", "content": message, "type": self.message_type}
    
    def load_chat_message(self, message, message_placeholder):
        return message_placeholder.markdown(message)