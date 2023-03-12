import os
import streamlit as st 
from seams.bgs_tools import create_subdirectory
from seams.video_tools import get_video_info, convert_codec, extract_frames, video_player, select_random_frames
from seams.datastorage import DataStore, YamlStorage
from seams.seafloor import substrates, phytobenthosCommonTaxa
from seams.markers import dotpoints_grid


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

#
ds_survey = DataStore(YamlStorage(file_path=SURVEY_FILEPATH))

#

current_surveyID = ds_survey.storage_strategy.data['current_surveyID']
current_station = ds_survey.storage_strategy.data['current_station']


substrates = [k[0] for k in substrates]
phytobenthosCommonTaxa = [k for k in phytobenthosCommonTaxa]

frames = ds_survey.storage_strategy.data['surveys'][current_surveyID]['stations'][current_station]['media']['frames']

with st.expander(
    label='**Benthic interpretation**',
    expanded=True
    ):

 
    header_col1, header_col2, header_col3, header_col4, header_col5 = st.columns(5)
    with header_col1:
        frameID = st.selectbox(
            label='**frames**',
            options=frames
            )
        if frameID:
            frame_filepath = frames[frameID]

    with header_col2:
        n_rows = st.slider(label='n Rows', min_value=3, max_value=5, )
    with header_col3:
        enable_random = st.checkbox(label='enable random', value=False)
    with header_col4:
        noise_percent = st.slider(label='pepper and salt noise', min_value=0.0, max_value=1.0, step=0.1)


    #with col2:
    #    st.checkbox(label='randomize dotpoints', value=False)
    #    st.checkbox(label='enable AI', value=False)

    with header_col5:
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
    
    if frame_filepath:
        # Select the image file
        with st.spinner("Creating dotpoints over image frame"):
                
            modified_image = dotpoints_grid(
                
                filepath=frame_filepath,
                n_rows=n_rows,
                enable_random=enable_random,
                noise_percent=noise_percent
                )
            
        with vcol1:

            if modified_image is not None:
                st.image(
                    modified_image, 
                    use_column_width=True,
                    )
        with vcol2:
            #selected_frame = st.selectbox(label='current frame', options=[f'frame {i+1}' for i in range(0,10)])

            substrates = st.selectbox(
                label='Susbstrates',
                options=substrates )
            
            taxons = st.multiselect(
                label='Taxons', 
                options=phytobenthosCommonTaxa)
            
            with st.container():
                is_all = st.checkbox(
                    label = 'select all', 
                    value=False)
                selected_dotPoints = st.multiselect(
                    'dotPoint presence', 
                    options=[f'{i+1}' for i in range(0,10)])

            st.markdown('---')
            with st.expander(label='extra occurrences'):
                extra_ocurrences =  st.multiselect(
                    label='**ocurrences**',
                    
                    options=phytobenthosCommonTaxa
                )

            
                shells = st.selectbox(label='SGU Limecola baltica shell', options={'no':0, 'förekommande':1, 'måttligt':2,'rikligt':3})
                krypspår = st.selectbox(label='Krypspår', options={'no':0, 'förekommande':1, 'måttligt > 10%':2,'rikligt > 50%':3})
                sandwave = st.number_input(label='Sandwave (cm)',min_value=-1.0, max_value=500.0, step=1.0, value=-1.0)
                frame_flags = st.multiselect(label = 'flags', options=['Dålig bildkvalitet', 'Dålig sikt/vattenkvalitet'])
                other_presences= st.multiselect(label='other presences', options=['fish', 'trash can', 'dolphin'])
                fieldNotes = st.text_area(label='Interpretation Notes')

