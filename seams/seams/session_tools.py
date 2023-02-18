import streamlit as st

def get_session_state_value(key:str):

    """If `key` exist in `st.session_state` return its value else None

    Args:
        key (str): Key to search in st.session_state

    Returns:
        _type_: _description_
    """
    if key in st.session_state:
        return st.session_state[key]



def show_selected_station_details():       

    # Add to new function
    user = get_session_state_value('user')
    surveyID = get_session_state_value('surveyID')
    n_stations = get_session_state_value('n_stations')
    selected_station = get_session_state_value('selected_station')
    stations_done = get_session_state_value('stations_done')

    if surveyID:
        surveyID = st.session_state['surveyID']

    with st.sidebar.expander(label='**Working session:**', expanded=True):          

        # Update sidebar
        st.markdown(f"user: **{user}**")
        if surveyID:
            st.markdown(f"survey ID: **{surveyID}**")
        else:
            st.markdown(f'survey ID: **< not defined >**')

        if n_stations:
            st.markdown(f'n stations: **{n_stations}**')
        else:
            st.markdown(f'n stations: **< not defined >**')

        if selected_station:
            st.markdown(f"Selected station: **{selected_station}**")
        else:
            st.markdown(f'Selected station: **< not defined >**')

        if stations_done and n_stations:
            n_done = len(stations_done)
            st.metric(label='**stations done:**', value=n_done, delta= n_done-n_stations)
        else:
            st.metric(label='**stations done:**', value=0, delta= n_stations)
            
    #TODO: remove this is just for development
    with st.sidebar.expander(label='**Development data:**', expanded=False):
        st.json(st.session_state)



