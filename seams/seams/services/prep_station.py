import os
import streamlit as st 
from seams.bgs_tools import create_subdirectory
from seams.video_tools import get_video_info, convert_codec, extract_frames, video_player, select_random_frames
from seams.datastorage import DataStore, YamlStorage


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

ds_survey = DataStore(YamlStorage(file_path=SURVEY_FILEPATH))


def load_video(filepath:str):
    assert os.path.isfile(filepath)

    video_file = open(filepath, 'rb')
    video_bytes = video_file.read()
    return video_bytes

def main():

    data = ds_survey.storage_strategy.data
    surveyID = data['current_surveyID']
    _current_station = data['current_station']
    stations = [s for s in data['surveys'][surveyID]['stations']]
    

    st.title('Station preprocessing')
    with st.container():
        col1, col2 = st.columns([1,1], gap="medium")

        with col1:
            current_station = st.selectbox(
                label='**current station**',
                options=stations,
                index=stations.index(_current_station))
            data['current_station'] = current_station
            # update current station
            st.session_state['current_station'] = current_station

            media = data['surveys'][surveyID]['stations'][current_station]['media']

            if 'video' in media:
                current_video = st.selectbox(
                    label='**video**',
                    options=media['video']
                    )
                _current_video = {current_video: media['video'][current_video] }
                data['current_video'] = _current_video
                st.session_state['current_video'] = _current_video
                #
                video_name = os.path.basename(media['video'][current_video])
                
                video_filepath = os.path.join(VIDEOS_DIRPATH, video_name)
                

                video_info =  get_video_info(video_path=video_filepath)
                with st.expander(label='**video info**', expanded=True):
                    if video_info:
                        st.write(video_info)
                        _vcodec = video_info['codec']
                        if _vcodec != "avc1":
                            with st.form(
                                key='convert_video_form',
                                clear_on_submit=True):
                                convert_video_codec_btn = st.form_submit_button(
                                    label='convert to video codec H.264',
                                    )
                                
                                if convert_video_codec_btn:
                                    with st.spinner():
                                        converted_video_filename = 'SEAMS__{video_name}'
                                        converted_video_filepath = os.path.join(VIDEOS_DIRPATH, converted_video_filename )
                                        video_conversion_done = convert_codec(
                                            input_file=video_filepath,
                                            output_file=converted_video_filepath
                                            )
                                        
                                        
                                        if video_conversion_done:
                                            # TODO: ensure properly error handling
                                            converted_video = {converted_video_filename: converted_video_filepath}
                                            st.success(f'Video codec conversion successful. Output file: {converted_video_filepath}')
                                            data['surveys'][surveyID]['stations'][current_station]['media']['video'][converted_video_filename] = converted_video_filepath
                                            data['current_video'] = converted_video
                                            st.session_state['current_video'] = converted_video
                                            video_filepath = converted_video_filepath
                                            video_name = converted_video_filename
                                            _current_video = converted_video

                                            ds_survey.store_data(data=data)
                        else:
                            ds_survey.store_data(data=data)               
                with st.form(key='extract_frames_form', clear_on_submit=True):
                    submit_extract = st.form_submit_button('extract video frames every 5 sec')
                    if submit_extract:
                        current_video_frames_dirpath = create_subdirectory(FRAMES_DIRPATH, video_name)
                        current_video_frames = {video_name: current_video_frames_dirpath}
                        
                        with st.spinner():
                                
                            frames = extract_frames(
                                video_filepath=video_filepath, 
                                frames_dirpath= current_video_frames_dirpath)
                            
                        
                            ds_survey.storage_strategy.data['current_video_frames'] = current_video_frames
                            ds_survey.store_data(ds_survey.storage_strategy.data)

                        st.success('frames available in: {}'.format(current_video_frames_dirpath))

                        with st.spinner():
                            if frames:
                                # TODO: deleted all the non random selected frames
                                random_frames = select_random_frames(
                                    frames=frames, 
                                    num_frames=10)
                                
                        if random_frames:
                            ds_survey.storage_strategy.data['surveys'][surveyID]['stations'][current_station]['media']['frames'] = random_frames
                            ds_survey.store_data(data=ds_survey.storage_strategy.data)

                            st.write(random_frames)

                            key_frames = st.multiselect(
                                label = 'selected random frames',
                                options= frames,
                                default= random_frames
                                )
                        
                        
        with col2:
            with st.expander(label='**show station data**', expanded=False):
                station = data['surveys'][surveyID]['stations'][current_station]
                st.write(station)
        

    
    if _vcodec == "avc1":

        with st.expander(label='**video player**'):
            pass
    
    st.write(ds_survey.storage_strategy.data)

# --
# -------------------------------------------------------
main()
