import os
from typing import Dict, Callable
import yaml
from dataclasses import dataclass, field
import chardet


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
        self.data = data

    def load_data(self):
        """Loads the data from the storage strategy into the `data` attribute."""
        pass

    def update_data(self, update_func: Callable):
        """Updates the data in the storage strategy using the given update function.

        Args:
            update_func (Callable): A function that takes the current data as input and returns the updated data.
        """
        self.data = update_func(self.data)

    def delete_data(self):
        """Deletes the data stored in the storage strategy."""
        self.data = {}


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
        file_path (str): The path to the YAML file to store the data in.
    """

    file_path: str = field(default_factory=str)

    def __post_init__(self):
        """Checks if the YAML file exists and loads it if it does, otherwise initializes the `data` property to an empty dictionary."""
        if os.path.isfile(self.file_path):
            self.load_data()
        else:
            self.data = {}

    def store_data(self, data:Dict):
        """Stores the data in the YAML file."""
        
        with open(self.file_path, 'w') as f:
            yaml.safe_dump(self.data, f, encoding='utf-8')
            self.data = data

    def load_data(self):
        """Loads the data from the YAML file into the `data` attribute of the `StorageStrategy` class."""
        try:
            with open(self.file_path, 'rb') as f:
                yaml_bytes = f.read()

            # Use chardet to detect the encoding of the yaml file
            result = chardet.detect(yaml_bytes)
            encoding = 'utf-8' if result['encoding'] is None else result['encoding']
            yaml_str = yaml_bytes.decode(encoding=encoding)

            self.data = yaml.safe_load(yaml_str)
        except (FileNotFoundError, IOError):
            self.data = {}

    def update_data(self, update_func: Callable):
        """Updates the data in the YAML file using the given update function.

        Args:
            update_func (Callable): A function that takes the current data as input and returns the updated data.
        """
        #self.load_data()
        self.data = update_func(self.data)
        self.store_data(data=self.data)

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
        data_store = DataStore(YamlStorage('data.yaml'))
        data = {'key': 'value'}
        data_store.store_data(data)
        loaded_data = data_store.load_data()
        ````

    Attributes:
        storage_strategy (StorageStrategy): The storage strategy used to store and retrieve data.
    """
    storage_strategy: StorageStrategy

    def store_data(self, data:Dict):
        """Stores the given data using the current storage strategy.

        Args:
            data (Dict): The data to store.
        """
        self.storage_strategy.data = data
        self.storage_strategy.store_data(data=self.storage_strategy.data)

    def load_data(self) -> Dict:
        """Loads the data from the current storage strategy into the `data` attribute of the `StorageStrategy` class and returns it."""
        self.storage_strategy.load_data()
        return self.storage_strategy.data

    def update_data(self, update_func: Callable):
        """Updates the data using the current storage strategy and the given update function.

        Args:
            update_func (Callable): A function that takes the current data as input and returns the updated data.
        """
        self.storage_strategy.update_data(update_func)

    def delete_data(self):
        """Deletes the data stored by the current storage strategy."""
        self.storage_strategy.delete_data() 

