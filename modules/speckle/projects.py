from dotenv import load_dotenv

from modules.speckle.data_handler.base_handler import BaseHandler

from specklepy.api.client import SpeckleClient
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport
from specklepy.api.wrapper import StreamWrapper
from specklepy.api import operations
from specklepy.serialization.base_object_serializer import BaseObjectSerializer
from specklepy.logging.exceptions import GraphQLException

import os

load_dotenv()

class ProjectsOverview:

    """
    This class contains all the projects that are available for the SpeckleHandler.
    """

    # define the list of projects here
    PROJECTS = [
        {'name': 'Revit Demo Haus',
            'url': 'https://app.speckle.systems/projects/xxx/models/xxx'},
        ]

    def __init__(self):
        """ loads projects as dictionary with name and url as key value pairs"""
        self.projects = {obj["name"]: obj["url"] for obj in self.PROJECTS}
    
    def get_url(self, project_name):
        """ returns the url of the project with the given name"""
        return self.projects[project_name]
    
    def get_default_project(self):
        """ returns the first project in the list"""
        return self.projects[0]


class SpeckleProject:

    """
    This class handles the operations of a single Speckle project.
    For the output of data, see speckle_data.py
    """

    def __init__(self, name = None, url = None):
        """ provide the SpeckleProject with a name and a url or a project name from the ProjectsOverview"""
        self.name = name
        if url is not None:
            self.url = url
        else:
            self._load_from_projects(name)
        self.json = None

    def _load_from_projects(self, name):
        """ loads the url from the ProjectsOverview"""
        projects = ProjectsOverview()
        try:
            self.url = projects.get_url(name)
        except KeyError:
            KeyError(f"Project {name} not found in ProjectsOverview")

    def load_json(self):
        """ loads the json data from the Speckle base object"""
        serializer = BaseObjectSerializer()
        _, self.obj_dict = serializer.traverse_base(self.base_obj)
        return self.obj_dict

    def _load_auth_token(self):
        """
        loads auth_token from .env
        """
        self.auth_token = os.environ.get("SPECKLE_AUTH_TOKEN")

    def get_commit_data(self, commit_url: str) -> Base:
        """ gets the commit data from the Speckle API and returns it as Base object,
        supports old and new Speckle format"""
        version = self.identify_oldnew_speckle(commit_url)
        if version == "old":
            commit_data = self.get_commit_data_old(commit_url)
        elif version == "new":
            commit_data = self.get_commit_data_new(commit_url)
        return commit_data

    def get_commit_data_old(self, commit_url: str) -> Base:
        """
        get the commit data as Base object, based on the old Speckle version
        """
        # load Speckle API token
        self._load_auth_token()

        version = self.identify_oldnew_speckle(commit_url)
        if version=="old":
            client = SpeckleClient(host="app.speckle.systems")
        elif version=="new":
            client = SpeckleClient(host="speckle.xyz")

        client = SpeckleClient(host="speckle.xyz")
        client.authenticate_with_token(self.auth_token)

        # get Speckle Stream Wrapper
        wrapper = StreamWrapper(commit_url)
        # Initialize a server transport
        transport = ServerTransport(client=client, stream_id=wrapper.stream_id)

        # Get the commit
        try:
            commit_obj = client.commit.get(wrapper.stream_id, wrapper.commit_id)
        except GraphQLException as e:
            raise ValueError(f"Error while getting commit: {e}")

        # load the base object
        self.base_obj = operations.receive(commit_obj.referencedObject, transport)
        return self.base_obj
    
    def get_commit_data_new(self, commit_url: str) -> Base:
        """ get the commit data as Base object, based on the new Speckle version"""
        # load Speckle API token
        self._load_auth_token()
        
        client = SpeckleClient(host="app.speckle.systems")
        client.authenticate_with_token(self.auth_token)

        # get Speckle Stream Wrapper
        wrapper = StreamWrapper(commit_url)

        # Fetch commit and create a transport for operations
        if wrapper.commit_id is None:
            stream = client.stream.get(wrapper.stream_id)
            model = next((branch for branch in stream.branches.items
                        if branch.id == wrapper.model_id), None)
            commit = model.commits.items[0] if model else None

        transport = ServerTransport(client=client, stream_id=wrapper.stream_id)

        # Get the commit
        self.base_obj = operations.receive(obj_id=commit.referencedObject,remote_transport=transport)
        
        # try:
        #     # Retrieve and process the referenced object
        #     self.base_obj = operations.receive(obj_id=commit.referencedObject,remote_transport=transport)
        # except GraphQLException as e:
        #     raise ValueError(f"Error while getting commit: {e}")
        
        return self.base_obj
    
    def identify_oldnew_speckle(self, commit_url: str) -> str:
        """ identifies if the commit_url is from the old or new speckle version"""
        # check URL for old or new Speckle version
        if "speckle.xyz" in commit_url:
            return "old"
        elif "app.speckle.systems" in commit_url:
            return "new"
        else:
            raise ValueError("URL not recognized as Speckle URL")
        

    def get_categories(self) -> list[str]:
        """ returns the categories of the project"""
        if not hasattr(self, "base_obj"):
            self.get_commit_data(self.url)
        self.categories = self.base_obj.get_dynamic_member_names()
        return self.categories
    
    def get_basehandler(self) -> BaseHandler:
        """ returns the basehandler with the base_obj"""
        # check that base_obj is already loaded
        if not hasattr(self, "base_obj"):
            self.get_commit_data(self.url)
        # create basehandler
        self.basehandler = BaseHandler(self.base_obj)
        return self.basehandler
    
    def get_project_information(self) -> Base:
        """ extracts the project information as base object"""
        # check the version
        version = self.identify_oldnew_speckle(self.url)
        # potentially load the base object
        if not hasattr(self, "base_obj"):
            self.get_commit_data(self.url)

        # get the project information
        if version == "old":
            project_info = self.base_obj["@Projektinformationen"][0]
        elif version == "new":
            project_info = self.base_obj["@Project Information"][0]
        return project_info