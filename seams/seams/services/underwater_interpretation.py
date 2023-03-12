import streamlit as st
from seams.datamodels import DotPoint
from PIL import Image
from seams.markers import create_bounding_box, floating_marker, markers_grid



surveyName = 'survey21'

def check_session_key(session_key:str):
    """ Checks if session_key exist in the streamlit st.session_state

    Args:
        session_key (str): session key exist check

    Returns:
        Any : value of the session_key if existe else empty string. The empty string will triger False on validation.
    """
    if session_key in st.session_state:
        return  st.session_state.get(session_key)
    #else:
    #    return 


if 'frame_id' not in st.session_state:
    st.session_state['frame_id'] = 1
if 'survey_name' not in st.session_state:
    st.session_state['survey_name'] = 'Survey name'
if 'station_name' not in st.session_state:
    st.session_state['station_name'] = 'Station 01'


@st.cache()
def dotpoints_grid(
    image_file, 
    filepath:str,
    n_rows = 3,
    enable_random = False,
    noise_percent = 0.0
):
    if image_file is not None:
        dotpoints = []
        frame_id = 1
        
        image = Image.open(filepath)       

        # create bounding box polygon
        bbox = create_bounding_box(image=image)


        centroids = markers_grid(bbox, n_rows=n_rows, enable_random=enable_random, noise_percent=noise_percent)
   
        for centroid in centroids:
            dotpoint = DotPoint(frame_id=frame_id, x=int(centroid.x), y=int(centroid.y))
            dotpoints.append(dotpoint)
                    
        # Add the floating button to the image
        modified_image = floating_marker(image, dotpoints=dotpoints)
               
        return modified_image
        
        



def main(  n_rows = 3,  enable_random = False, noise_percent = 0.0):
    stations = check_session_key('stations')
    stationName = check_session_key('stationName')
    surveyName = check_session_key('surveyName')

    st.sidebar.markdown('---')
    st.sidebar.subheader(f"Survey: **{st.session_state['surveyName']}**")


    station = st.sidebar.selectbox(
        label="Station",
        options=stations)


    sc1, sc2 = st.sidebar.columns(2)

    sc1.metric(label='n stations', value=len(stations), )
    sc2.metric(label='done', value=1, delta= 1 )

    header_expander = st.expander(label='advanced configutation')
  
    with header_expander:
        _, header_col2, header_col3, header_col4, _ = st.columns(5) 
        with header_col2:
            n_rows = st.slider(label='n Rows', min_value=3, max_value=5, )
        with header_col3:
            enable_random = st.checkbox(label='enable random', value=False)
        with header_col4:
            noise_percent = st.slider(label='pepper and salt noise', min_value=0.0, max_value=1.0, step=0.1)


    # Select the image file
    image_file = st.sidebar.file_uploader("Choose an image file", type=['jpg', 'png'])

    

    with st.spinner("Creating dotpoints over image frame"):
            
        modified_image = dotpoints_grid(
            image_file=image_file, 
            filepath='/home/begeospatial/develop/dockers/poetry-havsmus/poetry_havsmus/survey_data/raw/media/photos_jpg/nmi18_11003 0 Lat 6233003.18 Lon 637273.97 Pan -150.0 Tilt 0.0 Hdg 16.0 18_07_26 13_24_040001.JPG',
            n_rows=n_rows,
            enable_random=enable_random,
            noise_percent=noise_percent
            )
            
    col1, col2 = st.columns([4,1])
    
    with col1:

        if modified_image is not None:
            st.image(
                modified_image, 
                use_column_width=True,
                )
    with col2:
        selected_frame = st.selectbox(label='current frame', options=[f'frame {i+1}' for i in range(0,10)])
        is_all = st.checkbox(label = 'select all', value=False)
        selected_dotPoints = st.multiselect('dotPoint presence', options=[f'{i+1}' for i in range(0,10)])
        taxons = st.multiselect(label='Taxons', options=['s1','s2', 's3'])
        substrates = st.selectbox(label='Susbstrates',options={
            "UkSu": "Unknown Substrate",
            "HaCl": "Hard Clay",
            "Mu": "Mud (<0.002mm)",
            "Si": "Silt (0.002-0.06mm)",
            "Sa": "Sand (0.06-2mm)",
            "Gr": "Gravel (2-20mm)",
            "St": "Stones/Pebbles (20-60mm)",
            "LaSt": "Large Stones/Pebbles (60-200mm)",
            "Bo": "Boulders (200-600mm)",
            "LaBo": "Large Boulders (>600mm)",
            "SoRo": "Solid Rock",
            "ShGr": "Shell Gravel",
            "Blank": "Blank",
            "UcSu": "Uncolonised Substrate"} )
        shells = st.selectbox(label='SGU Limecola baltica shell', options={'no':0, 'förekommande':1, 'måttligt':2,'rikligt':3})
        krypspår = st.selectbox(label='Krypspår', options={'no':0, 'förekommande':1, 'måttligt > 10%':2,'rikligt > 50%':3})
        sandwave = st.number_input(label='Sandwave (cm)',min_value=-1.0, max_value=500.0, step=1.0, value=-1.0)
        frame_flags = st.multiselect(label = 'flags', options=['Dålig bildkvalitet', 'Dålig sikt/vattenkvalitet'])
        other_presences= st.multiselect(label='other presences', options=['fish', 'trash can', 'dolphin'])
        fieldNotes = st.text_area(label='Interpretation Notes')


#if __name__ == "__main__":
main()