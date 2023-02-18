import os
import sys
import toml
import psycopg2
from pathlib import Path
from collections import OrderedDict
import streamlit as st
from seams.photo_utils import read_photos, test_read_photos
from seams.bgs_tools import build_activities_menu, get_available_activities


st.set_page_config(layout='wide')

# Utility dictionary
session_initialization = OrderedDict({
    'Session initialization':{
        "name": "Session initialization",
        "description": "Data initialization",
        "url": "./seams/services/session_init.py",
}})



@st.cache
def initialize_seams():
    """Load the configuration from the `seams.toml`file and update the session state with the config
    """
    toml_path = os.path.join(Path(__file__).resolve().parents[0], 'seams', 'seams.toml')
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
    LOGO_SIDEBAR_URL = st.session_state['logos']['LOGO_SIDEBAR_URL']
    LOGO_ODF_URL = st.session_state['logos']['LOGO_ODF_URL']
    SERVICES_YAML_URL = st.session_state['environment']['SERVICES_YAML_URL']
    SERVICES_DIRPATH = st.session_state['environment']['SERVICES_DIRPATH']

    st.sidebar.image(LOGO_SIDEBAR_URL)
    sidebar_expander = st.sidebar.expander(label='**SEAMS** - PLAN SUBSIM', )
    #session_expander = st.sidebar.expander(label='Current session')

    with sidebar_expander:
        st.title('SEAMS')
        st.subheader('SEafloor Annotation Module Support')
        st.markdown(
            """ *[PLAN-SUBSIM](https://oceandatafactory.se/plan-subsim/)*
            a national implementation of a PLatform for ANalysis of SUBSea IMages.
            """)
        st.image(LOGO_ODF_URL)



    # Load the yaml with core services as activities    
    core_activities =  get_available_activities(
        filepath=os.path.abspath(SERVICES_YAML_URL)        
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
        if 'logos' in st.session_state:
            main()
        else:
            main()
            st.button(label='REFRESH APP')

    else:
        st.error('The app failed initialization. Report issue to mantainers in github')