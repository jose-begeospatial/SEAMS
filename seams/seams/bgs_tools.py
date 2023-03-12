# Credits: Be GeoSpatial
# Mantainers: José Beltrán
# License MIT

import os
import sys
import yaml
from typing import Any
from importlib.util import module_from_spec, spec_from_file_location
from collections import OrderedDict
import streamlit as st
import h3
from pyproj import Proj, transform


def load_yaml(filepath: str):
    """Loads a yaml file.

    Can be used as stand alone script by

    :params filepath: file path to the yaml file to be loaded.

    :usage:

       `load_yaml.py --filepath /file/path/to/filename.yaml`

    :return: a dictionary object
    """
    assert os.path.isfile(filepath)

    if not os.path.isfile(filepath):
       raise IOError(f"`filepath` missing = `{filepath}`, ensure `filepath` exist or "
              "if standalone `--filepath /file/path/filename.yaml` argument is given.")
        
    else:
        with open(filepath, 'r') as file_descriptor:
            try:
                yaml_data = yaml.safe_load(file_descriptor)
            except Exception as msg:
                raise IOError(f'File `{filepath}` loading error. \n {msg}')
            else:
                return yaml_data



def get_available_services(services_filepath: str)->OrderedDict[Any, Any]:
    """Retrieves from a yaml file the services to show to the user as a sidebar menu.
    Used to create multipages apps using Streamlit.

    Returns: 
        actitivities ordered dictionary. 
    """
  
    assert os.path.isfile(services_filepath)

    available_activities_list = load_yaml(filepath=os.path.abspath(services_filepath))

    if available_activities_list:

        activities_dict = OrderedDict(
            {item['name']: item for item in available_activities_list})
    
        return activities_dict
    else: 
        return None

def check_service_path(services_dirpath, default_dirpath:str = '/seams/seams/services/' ):
    """Sanity check to build the correct paths for the app services.

    Args:
        services_dirpath (_type_): path string  for the services directory
        default_dirpath (str, optional): _description_. Defaults to '/seams/seams/services/'.

    Returns:
        str: `services_dirpath` if exist else `None`
    """

    if os.path.isdir(services_dirpath):
        return services_dirpath
    else:
        # Try to construct dirpath
        working_dir = os.getcwd()
        services_dirpath = os.path.join(working_dir, default_dirpath)
        if os.path.isdir(services_dirpath):
            return services_dirpath


def script_as_module(module_filepath: str, services_dirpath: str):
    """Loads a python script, register as module, and makes it available for the package path. Super geek powers!

    Usually used to populate services in a streamlit app.
   
    :return: True if success else False
    :credits: https://github.com/drjobel/turpy/blob/develop/src/turpy/utils/__init__.py 
    """
    
    assert isinstance(services_dirpath, str)
    assert isinstance(module_filepath, str)
    assert os.path.isdir(os.path.abspath(services_dirpath))

    # 
    module_filepath = os.path.join(services_dirpath, module_filepath)

    #assert os.path.isfile(os.path.abspath(module_filepath))

    # Loading by script module
    module_name = os.path.basename(
        os.path.abspath(module_filepath)).replace('.py', '')
    
    # type: ignore
    spec = spec_from_file_location(
        name=module_name,
        location= module_filepath,
        submodule_search_locations=[services_dirpath]
    )

    if spec:            
        try:
            module = module_from_spec(spec)            
        except Exception as e:
            ImportError(str(e))
            return False
        else:
            spec.loader.exec_module(module)
            # Optional; only necessary if you want to be able to import the module
            # by name later.
            sys.modules[module_name] = module
            return True
    else:
        return False




def build_activities_menu(activities_dict: OrderedDict, label: str, key: str, services_dirpath: str, disabled:bool = False):
        activity_names = []
        selected_activity = None

        for _, task_dict in activities_dict.items():
            activity_names.append(
                (task_dict['name'], task_dict['url']))

        selection_tuple = st.sidebar.selectbox( 
            label=label,
            index=0,
            options= activity_names,
            format_func=lambda x: str(x[0]), 
            key=key, 
            disabled=disabled)

        if selection_tuple is not None:
            
            selected_activity, module_filepath = list(selection_tuple)
            # Super geek powers!
            
            script_as_module(module_filepath=module_filepath, services_dirpath = services_dirpath)

        return selected_activity, activities_dict






def get_h3_geohash(decimalLatitude:float, decimalLongitude:float, resolution:int=12):
    """ H3 geohash. Location as decimalLatitude and longitude coordinates in WGS84, returning the H3 geohash 
    at a default resolution 12 corresponding to a cell size of approximately 0.38km x 0.38km.

    Args:
        decimalLatitude (float): Latitude in decimal degrees
        decimalLongitude (float): Longitude in decimal degrees
        resolution (int, optional): Geohash at given resolution.  
            Defaults to 12 (which corresponds to a cell size approximately 0.38km x 0.38km).

    Returns:
        str : H3 geohash string 
    """
    return h3.geo_to_h3(decimalLatitude, decimalLongitude, resolution)


def reproject_coordinates(x_or_longitude:float, y_or_latitude:float, inProj:str = 'epsg:4326', outProj:str = 'epsg:3006')->tuple:
    """Reprojects the coordinates from `inProj` to `outProj` 
    By default is expecting decimalLatitude and decimalLongitude coordinates in WGS84 (`epsg:4326`)
        and outputs the coordinates in x, y using the SWEREF99TM (`epsg:3006`)
    
    Args:
        x_or_longitude (float): input decimal coordinates- longitude or X. 
        y_or_latitude (float): input decimal coordinates - latitude or Y. 
        inProj (str, optional): input spatial reference system as EPSG. Defaults to 'epsg:4326'.
        outProj (str, optional): output spatial reference system as EPSG. Defaults to 'epsg:3006'.

    Returns:
        coordinates_xy (tuple): reprojected coordinates (x, y)

    """
    _inProj = Proj(init=inProj)
    _outProj = Proj(init=outProj)

    # Convert coordinates
    coordinates_xy = transform(inProj, outProj, x_or_longitude, y_or_latitude)
    # x, y
    return coordinates_xy[0], coordinates_xy[1]


def get_h3_geohash_epsg3006(x:float,y:float, resolution:int=12):
    """ H3 geohash given coordinates in SWEREF99TM 

    Args:
        x (float): X decimal coordinate
        y (float): Y decimal coordinate
        resolution (int, optional): Geohash at given resolution. Defaults to 12.

    Returns:
        _type_: _description_
    """
    decimalLongitude, decimalLatitude= reproject_coordinates(x, y, inProj='epsg:3006', outProj='epsg:4326')
    # convert to geohash
    return get_h3_geohash(decimalLatitude, decimalLongitude, resolution)


def get_coordinates_epsg3006_from_geohash(geohash:str, outProj:str = 'epsg:3006'):
    # get the coordinates from geohash
    coordinates_yx = h3.h3_to_geo(geohash)
    inProj = Proj(init='epsg:4326')
    # convert coordinates to EPSG:3006
    coords_xy = transform(inProj, outProj, coordinates_yx[1], coordinates_yx[0])
    x = coords_xy[0]
    y = coords_xy[1]
    return x, y 



def create_subdirectory(path, subdir):
    """
    Creates a new subdirectory if it does not exist.

    Args:
        path (str): The path to the parent directory.
        subdir (str): The name of the subdirectory to create.

    Returns:
        str: The full path to the subdirectory.
    """

    # Create the full path to the subdirectory
    full_path = os.path.join(path, subdir)

    # Check if the subdirectory exists
    if os.path.isdir(full_path):
        print(f'Subdirectory {full_path} already exists')
    else:
        # Create the subdirectory if it does not exist
        try:
            os.mkdir(full_path)
            print(f'Subdirectory {full_path} created')
        except OSError as e:
            print(f'Error occurred while creating subdirectory: {e.strerror}')
            return None

    return full_path



