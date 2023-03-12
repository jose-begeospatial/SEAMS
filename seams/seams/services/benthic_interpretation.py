import os
import streamlit as st 
from seams.bgs_tools import create_subdirectory
from seams.video_tools import get_video_info, convert_codec, extract_frames, video_player, select_random_frames
from seams.datastorage import DataStore, YamlStorage
from seams.seafloor import substrates, phytobenthosCommonTaxa


# Globals

APP_DIRPATH = st.session_state['APP_DIRPATH']
DATA_DIRPATH = st.session_state['DATA_DIRPATH']
SERVICES_DIRPATH = st.session_state['SERVICES_DIRPATH']
ASSETS_DIRPATH = st.session_state['ASSETS_DIRPATH']
APP_SERVICES_YAML = st.session_state['APP_SERVICES_YAML']
USERS_FILEPATH = st.session_state['USERS_FILEPATH']
SURVEY_FILEPATH = os.path.join(DATA_DIRPATH, 'survey.yaml')
if 'SURVEY_FILEPATH' not in st.session_state:
    st.session_state['SURVEY_FILEPATH'] = SURVEY_FILEPATH

#
VIDEOS_DIRPATH = os.path.join(DATA_DIRPATH, 'survey', 'videos')
PHOTOS_DIRPATH = os.path.join(DATA_DIRPATH, 'survey', 'photos')
FRAMES_DIRPATH = os.path.join(DATA_DIRPATH, 'survey', 'frames')

surveyID = st.session_state['surveyID']
current_station = st.session_state['current_station']
current_video = st.session_state['current_video'] 

substrates = [k[0] for k in substrates]
phytobenthosCommonTaxa = [k for k in phytobenthosCommonTaxa]


ds_survey = DataStore(YamlStorage(file_path=SURVEY_FILEPATH))

frames = ds_survey.storage_strategy.data['surveys'][surveyID]['stations'][current_station]['media']['frames']

with st.expander(
    label='**Benthic interpretation**',
    expanded=True
    ):

    col1, col2, col3, col4 = st.columns([1,1,1,1])
  
    with col1:
        frameID = st.selectbox(
            label='**frames**',
            options=frames
            )
        if frameID:
            frame_filepath = frames[frameID]
    
    with col2:
        st.checkbox(label='randomize dotpoints', value=False)
        st.checkbox(label='enable AI', value=False)

    with col4:
        with st.container():
            #st.write('**dotpoints**')
            dotpoints = st.multiselect(
                label='**dotpoints done**',
                options= [
                
                '01',
                '02',
                '03',
                '04',
                '05',
                '06',
                '07',
                '08',
                '09',
                '10'],
                default=['01','03','08', '10']

            )
            
with st.container():
    vcol1, vcol2 = st.columns([5,1])
    
    with vcol1:
        if frame_filepath:
            st.image(frame_filepath, use_column_width='auto', )
    with vcol2:
        with st.container():
            #st.write('**substrates**')

            substrates = st.multiselect(
                label= '**substrates**',
                options= substrates
                )
        with st.container():
            #st.write('**species**')

            biota = st.multiselect(
                label='**species**',
                
                options=phytobenthosCommonTaxa
            )
        with st.container():
            #st.write('**dotpoints**')
            dotpoints = st.multiselect(
                label='**dotpoint**',
                options= [
                
                '01',
                '02',
                '03',
                '04',
                '05',
                '06',
                '07',
                '08',
                '09',
                '10']

            )
            st.checkbox(label='select all', value=False)
        
        st.markdown('---')
        with st.expander(label='extra occurrences'):
            extra_ocurrences =  st.multiselect(
                label='**ocurrences**',
                
                options=phytobenthosCommonTaxa
            )

        with st.expander(label='comments'):
            st.text_area(label='value comments only')

        


    