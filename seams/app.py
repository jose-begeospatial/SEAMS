import os
import sys
import toml
import psycopg2
from pathlib import Path
from collections import OrderedDict
import streamlit as st
from seams.bgs_tools import build_activities_menu, get_available_services
from seams.session_tools import show_selected_station_details

st.set_page_config(layout='wide')
# Set the Streamlit server address to a specific IP
#st.set_option('server.address', '172.16.238.2')

# Utility dictionary
session_initialization = OrderedDict({
    'Session initialization':{
        "name": "Session initialization",
        "description": "Data initialization",
        "url": "./seams/services/session_init.py",
}})


def initialize_seams():
    """Load the configuration from the `seams.toml`file and update the session state with the config
    """
    APP_DIRPATH = Path(__file__).resolve().parents[0]
    DATA_DIRPATH = os.path.join(APP_DIRPATH, 'data')
    SERVICES_DIRPATH = os.path.join(APP_DIRPATH, 'seams', 'services')
    ASSETS_DIRPATH = os.path.join(APP_DIRPATH, 'assets')
    APP_SERVICES_YAML = os.path.join(APP_DIRPATH, 'app_services.yaml')
    USERS_FILEPATH = os.path.join(DATA_DIRPATH, 'users.yaml')
    
    # 
    st.session_state['APP_DIRPATH'] = APP_DIRPATH
    st.session_state['DATA_DIRPATH'] = DATA_DIRPATH
    st.session_state['SERVICES_DIRPATH'] = SERVICES_DIRPATH
    st.session_state['ASSETS_DIRPATH'] = ASSETS_DIRPATH
    st.session_state['APP_SERVICES_YAML'] = APP_SERVICES_YAML
    st.session_state['USERS_FILEPATH'] = USERS_FILEPATH

    # toml_path with 
    toml_path = os.path.join(APP_DIRPATH, 'seams', 'seams.toml')   
    
    #
    with st.spinner(text='inititializing app'):        
        # load the seams.toml file with custom config for the App
        try:
            # load the seams.toml file from the parent directory.
            
            seams = toml.load(toml_path)
            # Update the session state with the config
            for k in seams:
                if k not in st.session_state:
                    st.session_state[k] = seams[k]
            return True
        except FileNotFoundError as e:
            st.error(f'The `seams.toml` file was not found in {toml_path}')
        except toml.TomlDecodeError as e:
            st.error(f"Error parsing the seams.toml file: {e}")
        except Exception as e:
            st.error(f'An error ocurred while initializing the app: {e}')

def main():

    if 'logos' in st.session_state:
        LOGO_SIDEBAR_URL = st.session_state['logos']['LOGO_SIDEBAR_URL']
        LOGO_ODF_URL = st.session_state['logos']['LOGO_ODF_URL']
    else:
        LOGO_SIDEBAR_URL = ""
        LOGO_ODF_URL = ""

    APP_SERVICES_YAML = st.session_state['APP_SERVICES_YAML']       
    SERVICES_DIRPATH = st.session_state['SERVICES_DIRPATH']
    
    if LOGO_SIDEBAR_URL: st.sidebar.image(LOGO_SIDEBAR_URL)
    sidebar_expander = st.sidebar.expander(label='**SEAMS** - PLAN SUBSIM')

    with sidebar_expander:
        st.title('SEAMS')
        st.subheader('SEafloor Annotation Module Support')
        st.markdown(
            """ *[PLAN-SUBSIM](https://oceandatafactory.se/plan-subsim/)*
            a national implementation of a PLatform for ANalysis of SUBSea IMages.
            """)
        if LOGO_ODF_URL: st.image(LOGO_ODF_URL)


    # Load the yaml with core services as activities    
    core_activities =  get_available_services(
        services_filepath=os.path.abspath(APP_SERVICES_YAML)        
    )
       
    build_activities_menu(
            activities_dict=core_activities, 
            label='**MENU:**', 
            key='activitiesMenu', 
            services_dirpath=SERVICES_DIRPATH,
            disabled=False
            )
    
    show_selected_station_details()
 

if __name__ == '__main__':
    if initialize_seams():
        main()
    else:
        st.error('The app failed initialization. Report issue to mantainers in github')