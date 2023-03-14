import os
import random
import cv2
import subprocess 
import tempfile
from urllib.parse import urlparse
from urllib.request import urlopen
import streamlit as st


def is_url(url:str):
    """Function to check if an url is valid or not

    Args:
        url (_type_): _description_

    Returns:
        _type_: _description_

    credits: https://github.com/ocean-data-factory-sweden/kso-utils/blob/5aeeb684dd7be86edcc8fbdccac07310f364bba2/tutorials_utils.py
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_video_info(video_path: str):
    """This function takes the path (or url) of a video and returns a dictionary with fps and duration information

    Args:
        video_path (str): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    '''
    
    :param video_path: a string containing the path (or url) where the video of interest can be access from
    :return: Two integers, the fps and duration of the video
    
    modified from: https://github.com/ocean-data-factory-sweden/kso-utils/blob/5aeeb684dd7be86edcc8fbdccac07310f364bba2/movie_utils.py
    '''

    size = 0
    cap = cv2.VideoCapture(video_path)
    # Check video filesize in relation to its duration
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # prevent issues with missing videos
    if int(frame_count)|int(fps) == 0:
        raise ValueError(
            f"{video_path} doesn't have any frames, check the path/link is correct."
        )
    else:
        duration = frame_count / fps

    duration_mins = duration / 60

    ##### Check codec info ########
    h = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = (
        chr(h & 0xFF)
        + chr((h >> 8) & 0xFF)
        + chr((h >> 16) & 0xFF)
        + chr((h >> 24) & 0xFF)
    )
  
    # Check if the video is accessible locally
    if os.path.exists(video_path):
        # Store the size of the video
        size = os.path.getsize(video_path)

    # Check if the path to the video is a url
    elif is_url(video_path):
        # Store the size of the video
        size = urlopen(video_path).length

    # Calculate the size:duration ratio
    sizeGB = size / (1024 * 1024 * 1024)
    size_duration = sizeGB / duration_mins

    return {
        'fps':fps, 
        'duration': duration,
        'frame_count': frame_count,
        'duration_mins': duration_mins,
        'size': size,
        'sizeGB': sizeGB,
        'size_duration': size_duration,
        'codec': codec,
        'video_name': os.path.basename(video_path),
        'video_path': video_path 
        }


def extract_frames_every_n_seconds(video_path:str, output_dir:str, n_seconds:int, total_frames:int, fps:float, prefix: str= 'frame')->dict:
    """ Extracts video frames every `n_seconds` and save them in `output_dir` temporary directory.

    Args:
        video_path (str): _description_
        output_dir (str): _description_
        n_seconds (int): _description_
        total_frames (int): _description_
        fps (float): _description_
        prefix (str, optional): _description_. Defaults to 'frame'.

    Returns:
        dict: _description_
    """

    temp_frames = {}
    step = int(n_seconds*fps)
    for i in range(0, total_frames, step):
        temp_frames[i] = []
        temp_file_descriptor, temp_file_path = tempfile.mkstemp(prefix=f'{prefix.strip().replace(" ", "_")}%06d_' % i, suffix=f'.png', dir=output_dir)
        os.close(temp_file_descriptor)
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        # new_file_path = #os.path.join(output_dir, "frame%06d.jpg" % i )
        subprocess.call(['ffmpeg', '-i', video_path, '-vf', 'select=gt(n\,{})'.format(i-1), '-pix_fmt', 'yuv420p', '-vframes', '1', '-f', 'image2', temp_file_path]) 
        temp_frames[i] = temp_file_path

    return temp_frames


def select_random_frames(frames:dict, num_frames:int = 10):
    """Randomly selects `num_frames` from the `frames` dictionary

    Args:
        frames (dict): video frames dictionary. Keys as frame number and values contain the filepath of the temporal frames
        num_frames (int): number of frames to sample. Defaults to 10.

    Returns:
        dict:  Keys as frame number and values contain the filepath of the sampled temporal frames.
    """
    selected_keys = random.sample(frames.keys(), num_frames)
    return {key:frames[key] for key in selected_keys}



st.cache_data(show_spinner=True)
def convert_codec(input_file, output_file)->bool:
    """
    Converts video codec from 'hvc1' to 'h264' using FFmpeg.

    Args:
        input_file (str): The path to the input video file.
        output_file (str): The path to the output video file.
    
    Returns:
        True if successful else False
    """

    # Check if FFmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        print('FFmpeg is not installed or is not in PATH')
        return False

    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f'Input file {input_file} does not exist')
        return False

    # Execute FFmpeg command
    try:
        subprocess.run(['ffmpeg', '-i', input_file, '-vcodec', 'libx264', '-acodec', 'copy', '-y', output_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error occurred while converting the file: {e.stderr.decode("utf-8")}')
        return False
    else:
        
        return True

    
st.cache_data(show_spinner=True)
def extract_frames(video_filepath, frames_dirpath):
        
    if video_filepath is not None and os.path.isfile(video_filepath):
        video_info =  get_video_info(video_path=video_filepath)
        st.write(video_info)
        temp_frames = extract_frames_every_n_seconds(
        video_path=video_filepath, 
        output_dir=frames_dirpath,
        n_seconds=5, 
        total_frames=video_info['frame_count'], 
        fps=video_info['fps']
        )

        if temp_frames:
            st.write(temp_frames)
        return temp_frames


def video_player(
    video_filepath, 
    marker_frame_positions = [100, 200, 500, 850, 1100, 1500, 2000, 3000, 4000]):
    """Video player requires video MP4 codec in H.264
    """
    #st.set_page_config(page_title="Video Player", page_icon=":film_strip", layout="wide")
    st.markdown('## Video timeline')
    # Create the custom component using st.beta_expander

    with st.expander("Show video frames"):
        st.write("""
        <link rel="stylesheet" href="https://cdn.plyr.io/3.6.2/plyr.css" />
        <video id="player" controls crossorigin playsinline>
            <source src="{}" type="video/mp4" />
        </video>

        <script src="https://cdn.plyr.io/3.6.2/plyr.js"></script>
        <script>
            const player = new Plyr('#player');
        var timeline = document.getElementById("timeline");
        var markers = document.getElementsByClassName("marker");
        var currentFrame = 0;
        var currentTime = 0;
        var totalFrames = player.duration * player.fps;
        var totalTime = player.duration;

        // Create the timeline
        for (var i = 0; i < totalFrames; i++) {{
            var tick = document.createElement("div");
            tick.classList.add("tick");
            timeline.appendChild(tick);
        }}

        // Create the markers
        for (var i = 0; i < {}.length; i++) {{
            var marker = document.createElement("div");
            marker.classList.add("marker");
            marker.setAttribute("data-frame", {}[i]);
            timeline.appendChild(marker);
        }}

        // Update the timeline and markers position
        player.on("timeupdate", event => {{
            currentFrame = Math.round(event.detail.plyr.currentTime * player.fps);
            currentTime = event.detail.plyr.currentTime;
            var minutes = Math.floor(currentTime / 60);
            var seconds = Math.floor(currentTime - minutes * 60);
            var time = minutes + ":" + seconds;
            timeline.style.marginLeft = - currentFrame + "px";
            for (var i = 0; i < markers.length; i++){{
                if (markers[i].getAttribute("data-frame") == currentFrame) {{
                    markers[i].innerHTML = currentFrame + "("+time+")";
                }}
            }}
        }});
        </script>
        <style>
            /* Add styles for the timeline and markers here */
            timeline {{
                position: relative;
                width: 100%;
                height: 20px;
                overflow: hidden;
                }}
                .tick {{
                    position: absolute;
                    width: 1px;
                    height: 20px;
                    background: #ccc;                    
                }}
                .marker {{
                    position:absolute;
                    width: 40px;
                    height: 20px;
                    background: #ff0000;
                    color: #fff;
                    text-align: center;
                    font-size: 12px;
                }}
        </style>
        <div id="timeline"></dic>
        """.format(video_filepath, marker_frame_positions, marker_frame_positions), unsafe_allow_html=True )





