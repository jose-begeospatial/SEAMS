import yaml
import os
from dataclasses import dataclass, field
from typing import Callable, Dict


@dataclass
class StorageStrategy:
    """A base class for storage strategies that manage data.

    Attributes:
        data (Dict): A dictionary representing the data being managed by the storage strategy.
    """
    data: Dict = field(default_factory=dict)

    def store_data(self, data: Dict):
        """Stores the given data in the storage strategy.

        Args:
            data (Dict): The data to store in the storage strategy.
        """
        pass    
    
    def load_data(self):
        """Loads the data from the storage strategy into the `data` attribute."""
        pass

    def update_data(self, update_func:Callable):
        """Updates the data in the storage strategy using the given update function.

        Args:
            update_func (Callable): A function that takes the current data as input and returns the updated data.
        """
        pass
        
    def delete_data(self):
        """Deletes the data stored in the storage strategy."""
        pass


@dataclass
class YamlStorage(StorageStrategy):
    """A storage strategy that stores and retrieves data in a YAML file.

    Use:

    ```
    def update_func(data):
        data.append({'new_key': 'new_value'})
        return data

    data_store = DataStore(YamlStorage('/path/to/data.yaml'))

    data_store.update_data(update_func)

    loaded_data = data_store.load_data()
    print(loaded_data)
    ```

    Args:
        StorageStrategy (_type_): The parent class that defines the common methods and properties of all storage strategies.
        file_path (str): The path to the YAML file to store the data in.
        data (Dict): The initial data to store in the YAML file. Default is an empty dictionary.
    """


    file_path: str = field(default_factory = str)
    data: Dict = field(default_factory=dict)


    def __post_init__(self):
        """Checks if the YAML file exists and loads it if it does, otherwise initializes the `data` property to an empty dictionary."""
        if os.path.isfile(self.file_path):
            self.load_data()
        else:
            self.data = {}

    def store_data(self):
        """Stores the data in the YAML file."""
        with open(self.file_path, 'w') as f:
            yaml.safe_dump(self.data, f)

    def load_data(self):
        """Loads the data from the YAML file into the `data` attribute."""
        try:
            with open(self.file_path, 'r') as f:
                self.data = yaml.safe_load(f)
        except (FileNotFoundError, IOError):
            self.data = {}
     

    def update_data(self, update_func:Callable):
        """Updates the data in the YAML file using the given update function.

        Args:
            update_func (Callable): A function that takes the current data as input and returns the updated data.
        """
        self.load_data()
        self.data = update_func(self.data)
        self.store_data()


    def delete_data(self):
        """Deletes the YAML file containing the data."""
        try:
            os.remove(self.file_path)
        except (FileNotFoundError, IOError):
            pass


@dataclass
class DataStore:
    """The DataStore class is responsible for managing the storage strategy used to store and retrieve data.

        Usage example: 
        ```
        data_store = DataStore(JsonStorage('data.json'))
        data = {'key': 'value'}
        data_store.store_data(data)

        loaded_data = data_store.load_data()
        ```

        Attributes:
            storage_strategy (StorageStrategy): The storage strategy used to store and retrieve data.
            data (Dict): The data being managed by the DataStore object.
        """
    storage_strategy: StorageStrategy    
    data: Dict = field(default_factory=dict)


    def store_data(self, data:Dict):
        """Stores the given data using the current storage strategy.

        Args:
            data (Dict): The data to store.
        """
        self.storage_strategy.data = self.data
        self.storage_strategy.store_data()
    
    def load_data(self):
        """Loads the data from the current storage strategy into the `data` attribute."""
        self.storage_strategy.load_data()
        self.data = self.storage_strategy.data
    
    def update_data(self, update_func:Callable):
        """Updates the data using the current storage strategy and the given update function.

        Args:
            update_func (Callable): A function that takes the current data as input and returns the updated data.
        """
        self.storage_strategy.update_data(update_func)
        self.data = self.storage_strategy.data
        
    def delete_data(self):
        """Deletes the data stored by the current storage strategy."""
        self.storage_strategy.delete_data()
        self.data = {}





 
