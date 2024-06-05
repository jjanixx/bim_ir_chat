from specklepy.objects.base import Base
from pandas import DataFrame
import pandas as pd

from .built_element_handler import BuiltElementsHandler


class BaseHandler:
    """ this class handles all operations regarding the overall base object"""

    def __init__(self, base: Base) -> None:
        """ initialize the BaseHandler with a Base object, load all detachable categories from the Base object"""
        if "@Types" in base.get_dynamic_member_names():
            # new Speckle data format
            self.base = base["@Types"]
        else:
            # old Speckle data format
            self.base = base
        self.categories = self.base.get_dynamic_member_names()

        # for old version: remove non-category elements
        for name in ["@Projektinformationen", "@Raster", "@Materialien"]:
            if name in self.categories:
                self.categories.remove(name)

    def get_parameters_from_category(self, selected_category: str) -> list[str]:
        # list of all parameters
        output_list = []
        # get all elements from the category
        category_elements = self.base[selected_category]
        # get the parameter_name


        if not hasattr(category_elements[0], "parameters") or category_elements[0]["parameters"] == None:
            # has no authoring software specific parameters
            parameters = self.get_notASparameter_values(selected_category)
        else:
            # has authoring software specific parameters
            ASparameters = self.get_ASparameters_from_category(selected_category)
       
        # add parameters to the output list
        output_list.extend(ASparameters)

        return sorted(output_list)

    def get_ASparameters_from_category(self, selected_category: str) -> list[str]:
        """outputs a list of all parameters in a certain category
        goes in the parameter list and looks for all (authoring software specific) parameters which are appended

        Args:
            self.base (Base): the commit data
            selected_category (str): the category to look for
        
        Returns:
            list[str]: list of all authoring software specific parameters in the category
        """
        # list of all parameters
        output_list = []
        # get all elements from the category
        category_elements = self.base[selected_category]
        # get the parameter_name

        # iterate over all elements
        for element in category_elements:
            assert hasattr(element, "parameters"), "No parameters found in element"
            # get all parameters from the element (which are in an extra list)
            parameters = element["parameters"].get_dynamic_member_names()
            # iterate over all parameters
            for parameter in parameters:
                # get the name of the parameter
                parameter_name = element["parameters"][parameter]["name"]
                # append if not already in the list
                if parameter_name not in output_list:
                    output_list.append(parameter_name)
        return sorted(output_list)

    def get_notASparameter_values(self, elements: list[Base], parameters: list[str]) -> DataFrame:
        """ not all Base Objectg have authoring software specific parameters, this function returns the parameters which are not AS specific"""
        raise ValueError("No Parameters folder there")

    def get_category_dataframe(self, category: str, parameters: list[str] = None) -> DataFrame:
        """Get the pandas dataframe by specifying the category

        Args:
            category (str): Name of category, must be in self.categories.
            parameters (list[str], optional): List of parameters to select. Defaults to None, then all parameters.

        Returns:
            DataFrame: Resulting dataframe.
        """

        # get list of base objects from the category
        entries = self.base[category]

        # potentially search for all parameters
        result_DF = self._create_dataframe_from_elements(entries, parameters)

        return result_DF

    def _create_dataframe_from_elements(self, base_list: list[Base], parameters: list[str] = None, sort: bool = True):
        """creates a dataframe for given elements, only adds the parameters in the list

        Args:
            elements (list[Base]): list of Base objects
            parameters (list[str]): list of parameters to select, if None all parameters are selected. Defaults to None.
            sort (bool, optional): sort the dataframe. Defaults to True.

        Returns:
            result_DF [list]: resulting list of data in 
        """

        # list of dictionaries, later translated into pandas
        result_data = []
        # iterate over elements and build up dictionary
        for AS_element in base_list:
            # initialize the RevitElementHandler
            element_handler = BuiltElementsHandler(AS_element)
            # get all parameters from the element
            data_dict = element_handler.get_AS_specific_parameters(parameters=parameters)
            # append the the parameters to the dictionary
            result_data.append(data_dict)
        # resulting data to DataFrame
        result_DF = DataFrame.from_dict(result_data)

        # sort the dataframe
        if sort:
            result_DF = self._clean_df(result_DF)

        return result_DF

    def _clean_df(self, df):
        """sorts the dataframe by columns with all values 0 or None at the end"""

        # Function to check if all values in a column are 0 or None
        def is_all_zero_or_none(column):
            return (column.fillna(0).replace('', 0) == 0).all()

        # Check if 'Name' column exists and remove it from the DataFrame for sorting
        name_column_exists = 'Name' in df.columns
        if name_column_exists:
            name_column = df['Name']
            df = df.drop(columns=['Name'])

        # Splitting the DataFrame into two based on the condition
        columns_to_move = [col for col in df if is_all_zero_or_none(df[col])]
        columns_to_keep = [col for col in df if col not in columns_to_move]

        # Re-add the 'Name' column at the beginning if it exists
        if name_column_exists:
            return pd.concat([pd.DataFrame(name_column), df[columns_to_keep], df[columns_to_move]], axis=1)
        else:
            return pd.concat([df[columns_to_keep], df[columns_to_move]], axis=1)
