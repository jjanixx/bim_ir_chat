from specklepy.objects.base import Base



class BuiltElementsHandler():

    def __init__(self, base: Base) -> None:
        """ initialize the BaseHandler with a Base object, load all detachable categories from the Base object"""
        assert  "Objects.BuiltElements" in base.speckle_type, f"Elment does not belong to BuiltElements, but is {base.speckle_type}"
        self.base = base
        self.parameters = self.base.get_dynamic_member_names()

    def get_category (self):
        return self.base["category"]

    def get_AS_specific_parameters(self, parameters = None):
        """ get all authoring software specific parameters from the Base Object
        
        Args:
            parameters (list): list of parameters to get from the Base Object

        Returns:
            dict: dictionary with all parameters
        """
        # dictionary with all data
        data_dict = {}
        if hasattr(self.base, "parameters"):
            # get all AS specific parameters from the Base Object
            as_parameters = self.base["parameters"].get_dynamic_member_names()
            # iterate over the parameters
            for param in as_parameters:
                name = self.base["parameters"][param]["name"]
                if parameters is None:
                    value = self.base["parameters"][param]["value"]
                    data_dict[name] = value
                elif name in parameters:
                    value = self.base["parameters"][param]["value"]
                    data_dict[name] = value
                else:
                    raise ValueError(f"Parameter {name} not found in the parameters list")
        return data_dict