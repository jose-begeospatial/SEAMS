import streamlit as st

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


def validate_session_keys(session_keys:list = ['surveyName', 'stationName',  'stations', 'machineObservation'])->bool:
    """Checks if all the listed `session_keys` exists in `st.session_state` and are not empty.

    Args:
        session_keys (list): session keys to check in streamlit `session_state`

    Returns:
        bool: True is all the session_keys exist and are not empty
    """

    validation = []
    if session_keys and len(session_keys)>=1:
        v = False            
        for k in session_keys:
            if not check_session_key(k):
                v = False
            else:
                v = True

            validation.append(v)
        
        return all(validation)
    else:
        return False

    