import uuid
import streamlit as st
import re
import psycopg2
from psycopg2 import sql
from seams.datamodels import Users
from seams.bgs_tools import get_h3_geohash, reproject_coordinates
from typing import Dict, List, Any, Callable
from seams.postgresql_tools import db_get_users_list, db_insert_new_user, db_table_exist
from itertools import count
from dataclasses import dataclass, field
from datetime import datetime 
import pandas as pd
import json


@dataclass
class DotPoint():
    """ DotPoint contains the information for the point intercept on the images for the visual methods.
    """
    id: int = field(default_factory=count().__next__, init=False)
    frame_id: int
    x_position: int
    y_position: int
    biota: List[str]
    substrates: str

    def __post_init__(self):
        self.id += 1
    def reset_id(self):
        self.id = 0


def db_create_stations_table(surveyID:str):
    with psycopg2.connect(**st.secrets['postgres']) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    f"""CREATE TABLE IF NOT EXIST stations__{surveyID} 
                    (guid SERIAL PRIMARY KEY,
                    siteName VARCHAR(50) UNIQUE NOT NULL, 
                    surveyGUID VARCHAR NOT NULL,
                    surveyName VARCHAR NOT NULL, 
                    decimalLatitude DECIMAL(9,6) NOT NULL,
                    decimalLongitude DECIMAL(9,6) NOT NULL,
                    countryCode VARCHAR(3) NOT NULL,
                    eventDate TIMESTAMP NOT NULL,
                    media jsonb, 
                    selectedFrames jsonb)""")
                conn.commit()
                st.success("Stations table created.")
            except psycopg2.Error as e:
                st.error(e)
                conn.rollback()

@dataclass
class Station():
    guid: str = field(init=False)
    siteName: str   # stationID
    surveyID: str
    countryCode: str 
    eventDate: datetime
    # 'EPSG:4326' -> WGS84
    locationID: str = field(init=False)
    geodeticDatum: str 
    decimalLatitude: float 
    decimalLongitude: float 
    # 'EPSG:3006' -> SWEREF99 TM  
    _Sweref99TmX: float = field(init=False)
    _Sweref99TmY: float = field(init=False)
    maximumDepthInMeters: float
    media: Dict[str, Dict[str, str]]
    selectedFrames: Dict[int, str] = field(default_factory= Dict[int, str])
    substrates: Dict[int, str] = field(default_factory= Dict[int, str])
    occurrences: Dict[int, List[str]] = field(default_factory= Dict[int, List[str]] )
    dotPoints: List[DotPoint] = field(default_factory= List[DotPoint])
    inProj: str = field(default='epsg:4326')
    outProj: str = field(default='epsg:3006')
    

    def __post_init__(self):
        self.guid = uuid.uuid4().hex
        #
        self.locationID = get_h3_geohash(
            self.decimalLatitude,
            self.decimalLongitude,
            )
        # Auto reproject latlon(epsg:4326) to epsg:3006
        coordinates_xy = reproject_coordinates(
            self.decimalLongitude, 
            self.decimalLatitude, 
            inProj=self.inProj, 
            outProj=self.outProj)

        self._Sweref99TmX = coordinates_xy[0]
        self._Sweref99TmY = coordinates_xy[1]


def db_insert_station(station: Station):
    # validate input
    station = Station(**station.dict())
    columns = station.schema().fields.keys()   #  columns = [col.name for col in station.schema().__fields__.values()]
    values = []
    for col in columns:
        value = getattr(station, col)

        if isinstance(value, datetime):
            #  if it's a datetime it converts it to a string format that is compatible with postgresql.
            value = value.strftime("%Y-%m-%d")   # "%Y-%m-%d %H:%M:%S"
        if isinstance(value, dict):
            # if it's a dict it converts it to json format that is compatible with postgresql.
            value = json.dumps(value)
        values.append(value)
    # prevent SQL injection
    insert = sql.SQL("INSERT INTO stations ({}) VALUES {}").format(
        sql.SQL(', ').join(map(sql.Identifier, columns)),
        sql.SQL(', ').join(map(sql.Identifier, values)),
        )
    
    try:            
        with psycopg2.connect(**st.secrets['postgres']) as conn:
            with conn.cursor() as cur:
                cur.execute(insert)
                conn.commit()

    except psycopg2.Error as e:
        st.error(e)


def validate_email(email:str)->bool:
    """
    Validate the email address using regular expression
    """
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if re.match(pattern, email):
        return True
    else: 
        return False


def header_status():
    """
    This function displays the status of the connection to a postgresql database in the header of a Streamlit app.
    It uses the Streamlit library to create a container with three columns and display different information in each column.
    The first column displays the title of the app.
    The second column displays a message indicating that the status of the connection is being displayed.
    The third column displays the result of the connection test, either "PostgreSQL Server running" or "PostgreSQL server connection failed"
    """
    
    with st.container():
            header_col1, header_col2, header_col3 = st.columns([3,1,1])
            with header_col1:
                st.markdown("### SEAMS- SEafloor Annotation Module Support")
            with header_col2:
                st.markdown('<H4>Database status:</H4>', unsafe_allow_html=True)
            try:
                with psycopg2.connect(**st.secrets['postgres']) as conn:
                    with header_col3:
                        if conn:
                            st.success('PostgreSQL Server running')
                            return True
            except psycopg2.Error as e:
                with header_col3:
                    st.error(f'seams-postgres:  {e}')
                    return False   
        

def show_new_user_form():
    new_user = None

    if 'affiliations' in st.session_state:
        affiliations = st.session_state['affiliations']
    else:
        affiliations = None

    userForm = st.form(key='userForm', clear_on_submit=True)
    with userForm:
        st.write('**Create a new user**')
        name = st.text_input("Name:", placeholder='user name')
        email = st.text_input("Email:", placeholder='user email address')
        affiliations = st.session_state['affiliations']

        if affiliations:
            affiliation = st.selectbox(
                label='Affilation:', 
                options=[ f'{k} - {v}' for k,v in affiliations.items()])
        else:
            affiliation = st.text_input("Affiliation", placeholder='user affiliation')


        apply_new_user_btn = st.form_submit_button(label='apply')

        if apply_new_user_btn:
            if not name or not email or not affiliation:
                st.error("All fields are required.")
            elif not validate_email(email):
                st.error("Invalid email address.")
            else:
                try:
                    new_user = Users(
                        name=name,
                        email=email,
                        affiliation=affiliation,
                    )
                    #
                    if db_insert_new_user(user=new_user):
                        st.success(f"**User:** `{new_user.name}` registered!")
                except Exception as e:
                    st.error(e)
                finally:
                    db_get_users_list()
                    return new_user
        

def current_user():
    users_list = db_get_users_list()

    __user = get_session_state_value('user')

    # Added +1 to account for the <new user> 
    
    with st.container():
        user_col1, user_col2 = st.columns(2)
        with user_col1:
            user = st.selectbox(
                "**Select a user:**", ['< new user >'] + users_list,
                index= users_list.index(__user) + 1 if len(users_list) > 0  else 0  
                )
            
            
            if user == '< new user >':
                with user_col2:
                    new_user = show_new_user_form()
                    if new_user:
                        users_list = db_get_users_list()
                user_col1.button('refresh')
            else:
                update_session_state('user', user)
                return user

def has_media(stations_dict:dict, media)->dict:
    """Function checks wether all the `siteNames` in the `stations_dict` has a `media` dictionary, 
    if it does not it adds the `media` key with a new dictionary with media as key and value an empty list, else
    adds a new dictionary with media as key and value an empty list.


    Args:
        stations_dict (dict): _description_
        media (str): _description_

    Returns:
        dict: _description_
    """
    for siteName in stations_dict:
        media_key = f'{media}'
        if 'media' not in stations_dict[siteName]:
            stations_dict[siteName]['media'] ={media_key: []}
        else:
            if media_key not in stations_dict[siteName]['media']: 
                stations_dict[siteName]['media'][media_key] = []
    return stations_dict

def update_session_state(key:str, value:Any)->bool:
    if key not in st.session_state:
        st.session_state[key] = value
    else:
        st.session_state[key] = value
    return True

def get_session_state_value(key:str):
    """If `key` exist in `st.session_state` return its value else None

    Args:
        key (str): Key to search in st.session_state

    Returns:
        _type_: _description_
    """
    if key in st.session_state:
        return st.session_state[key]


def show_surveyForm(
    delimeters:dict[str, str] = {'tab':'\t', 'comma':',', 'semicolon':';'}, 
    decimals:dict[str, str] = {'point':'.', 'comma':','}, 
    encodings:list[str] = ['utf-8', 'windows-1252'], 
    ):

    stations_df = None
    videos_df = None
    stations_dict = {}
    media = 'photos'
    survey_dict = {}

    with st.container():
        h1_col, _ , msg_col = st.columns(3)
        with h1_col:
            st.subheader('Survey details')
        with msg_col:
            priority_message = st.empty()
            missing_keys = check_required_session_keys()
            if len(missing_keys)== 0:
                priority_message.success('Survey initialization is done!')
            else:
                priority_message.warning(f'**Required**: {missing_keys}')
        
        top_col1,  top_col2, top_col3, top_col4  = st.columns([1,1,1,2])
        with top_col1:
            if 'surveyID' in st.session_state:
                session_id = st.session_state['surveyID']
                surveyID = st.text_input(label='**SurveyID:**', placeholder='Write the surveyID', value=session_id)
            else:
                surveyID = st.text_input(label='**SurveyID:**', placeholder='Write the surveyID')

            if surveyID:
                update_session_state(key='surveyID', value=surveyID)

        with top_col2:
            media = st.radio(label = '**Media:**', options=['photos', 'video'], index=0, horizontal=True)
            if media:
                st.session_state['media'] = media
        
        with st.form("survey form"):
            files_col1, files_col2 = st.columns([1,1])

            with files_col1:
                stationsFile_bytesio = st.file_uploader(label='**Stations file:**', type=['csv', 'tsv'])
            
            if media == 'video':
                with files_col2:
                    videosFile_bytesio = st.file_uploader(label='**Videos file:**', type=['csv', 'tsv'])
            else:
                videosFile_bytesio = None            

            col_delimiter, col_decimal, col_encoding, _, col_nstations = st.columns([1,1,1,1,1])
                    
            with col_delimiter:
                delimeter = st.selectbox(label='**delimeter:**', options=delimeters)
            with col_decimal:
                decimal = st.selectbox(label='**decimal:**', options=decimals)
            with col_encoding:
                encoding = st.selectbox(label='**encoding:**', options=encodings)

            apply_media_btn = st.form_submit_button(label='load files')

            if apply_media_btn:
                missing_keys = check_required_session_keys()

            
            expander_col1, expander_col2 = st.columns([1,1])
            with expander_col1:
                stations_expander = st.expander(label= f'**Stations table**')
            with expander_col2:
                videos_expander = st.expander(label='**Videos table**')
            

            if delimeter and decimal and encoding:
                _delimeter = delimeters[delimeter]
                _decimal = decimals[decimal]        

                if stationsFile_bytesio is not None:
                    update_session_state(key='surveyID', value=stationsFile_bytesio.name[:-4].split('__')[0])
                    
                    with st.spinner(text='loading stations ...'):
                        stations_df = pd.read_csv(
                            stationsFile_bytesio,
                            delimiter = _delimeter,
                            decimal= _decimal, 
                            encoding=encoding)

                    if isinstance(stations_df, pd.DataFrame):
                        stations_dict = {stn['siteName']: stn for stn in get_stations_data(df=stations_df)}
                        stations_dict = has_media(stations_dict=stations_dict, media=media)
                        n_stations = len(stations_dict)
                        update_session_state('n_stations', value=n_stations)
                        with top_col3:
                            st.metric('**n stations**', value= n_stations)

                if videosFile_bytesio is not None:
                    with st.spinner('Loading videos ...'):
                        videos_df = pd.read_csv(
                            videosFile_bytesio,
                            delimiter = _delimeter,
                            decimal= _decimal, 
                            encoding=encoding)
            
            with stations_expander:
                if isinstance(stations_df, pd.DataFrame):
                    st.dataframe(stations_df)                    

                with videos_expander:
                    if isinstance(videos_df, pd.DataFrame):
                        st.dataframe(videos_df)                        
                        videos_dict = get_videos_per_station(                            
                            videos_df=videos_df, 
                            callback=error_callback, 
                            )
                        update_session_state(key='videos_dict', value=videos_dict)

            with top_col4:
                if stations_dict is not None:
                    if 'stations_interpreted' not in st.session_state:
                        stations_to_interpret = stations_dict
                    elif len(st.session_state['stations_interpreted']) > 0:
                        stations_to_interpret = {k:v for k,v in stations_dict.items() if k not in st.session_state['stations_interpreted']}
                    else:
                        stations_to_interpret = stations_dict
               
                    selected_station = st.selectbox( 
                        '**Choose station for seafloor interpretation:**',
                        options=stations_to_interpret)
                    
                    if selected_station:
                        update_session_state(
                            key='selected_station',
                            value=selected_station
                            )
                        
                if surveyID:
                    with top_col3:
                        # st.info(f'**{surveyID}** loaded **{len(stations_dict)} stations**.')
                        survey_dict[surveyID] = stations_dict
                        update_session_state(key='survey_dict', value=survey_dict)                

                    if 'stations_dict' not in st.session_state:
                        update_session_state('stations_dict', value=stations_dict)                  

                else:
                    st.error("All fields are required.")
                
def has_all_required_columns(
    file_columns:list, 
    required_colnames: list):
    
    valid_cols = [col for col in file_columns if col in required_colnames]
    if len(valid_cols) == len(required_colnames):
        return True
    else:
        return False

def error_callback(error:str):
    st.error(error)

def videos_generator(subset:pd.DataFrame):
    pass
    

def get_videos_per_station(videos_df: pd.DataFrame, callback: Callable = error_callback) -> dict:
    required_colnames = ['siteName', 'filename', 'filepath']
    if not set(required_colnames).issubset(videos_df.columns):
        error_message = f"Missing required column names for video file. Required columns: {required_colnames}"
        callback(error_message)
        raise ValueError(error_message)        
    _videos = {}
    for siteName, subset in videos_df.groupby('siteName'):
        _videos[siteName] = dict(zip(subset['filename'], subset['filepath']))       
    return _videos


"""
def get_videos_per_station(stations_dict:dict, videos_df:pd.DataFrame, media: str, callback: Callable = error_callback)->dict:
    video_file_columns = videos_df.columns.values.tolist()
    is_file_valid = has_all_required_columns(file_columns=video_file_columns, required_colnames=['siteName', 'filename', 'filepath'])
    _videos = {}
    if is_file_valid:
        stations_names = videos_df['siteName'].unique()
        for siteName in stations_names:
            subset = videos_df.loc[videos_df['siteName'] == siteName]                        
            _videos[siteName] = (subset.apply(lambda x: {x['filename']:x['filepath']}, axis=1).reset_index(drop=True)) 
       
       
        for siteName in _videos:
            if siteName in stations_dict:
                stations_dict[siteName]['media'][media] = _videos[siteName]  #.append(_videos[siteName])
            else:
                callable(f'{siteName} not ins stations_dict')

    else:
        callback("Missing required column names for video file. Required columns: `['siteName', 'filename', 'filepath']`")

    return stations_dict

"""            
            

def get_stations_data(
    df:pd.DataFrame, 
    required_colnames: list  = [
        'siteName', 
        'decimalLatitude',
        'decimalLongitude',
        'geodeticDatum',
        'countryCode',
        'eventDate',
        'maximumDepthInMeters'
        ]):

    file_columns = df.columns.values.tolist()
    file_input_valid = has_all_required_columns(
        file_columns=file_columns, required_colnames=required_colnames)

    if file_input_valid:
        r = re.compile("measurementType", re.IGNORECASE)
        # regex to find all the columns names that matches `measurementType` at any place in the string.
        measurementType_cols = sorted(list(filter(r.search, file_columns )))
       
        results = {}
        for i, row in df.iterrows():
            for col in required_colnames:
                results[col] = row.get(col)
            
            if len(measurementType_cols)>0:
                measurements = {}
                for col in measurementType_cols:                    
                    measurements[col] = row[col]
                if len(measurements)>0:
                    results['measurementTypes'] = measurements
            yield results
    

    

def check_required_session_keys():

    required_keys = []
    missing_keys = []

    media = get_session_state_value('media')
    
    # quick fix as there is a refresh lag while having the s
    if media == 'video':
        required_keys =  ['user', 'surveyID', 'media', 'selected_station', 'survey_dict', 'videos_dict']
    if media == 'photos':
        required_keys =  ['user', 'surveyID', 'media', 'selected_station', 'survey_dict']

 
    for k in required_keys:
        if k not in st.session_state or not st.session_state[k] or st.session_state[k]=="":
            # Making it user friendly reading of varaiables.
            if k == 'selected_station':
                k = 'station'
            if k == 'survey_dict':
                k = 'stations file'
            if k == 'videos_dict':
                k = 'videos file'
            missing_keys.append(k)
    return missing_keys




def main():
    """
    Main function to display the header status, list of users, and allow creating a new user
    """
    # Check is Postgres server is running
    dbstatus = header_status()

    # 


    if dbstatus:
        #user = current_user()
        users_list = db_get_users_list()

        with st.container():
            user_col1, user_col2 = st.columns(2)
            with user_col1:
                user = st.selectbox("**Select a user:**", ['< new user >'] + users_list)
                if user == '< new user >':
                    with user_col2:
                        new_user = show_new_user_form()
                        if new_user:
                            users_list = db_get_users_list()
                    user_col1.button('refresh')


            if user and user != '< new user >':
                user = user.replace('"',"")
                if 'user' not in st.session_state:
                    st.session_state['user'] = user
                if 'user' not in st.session_state:
                    st.session_state['user'] = user

        #  Shows the survey form
        show_surveyForm()
                
    else:
        st.warning('Please ensure the PostgreSQL is up and running.')
                              
        
# ----------
main()

