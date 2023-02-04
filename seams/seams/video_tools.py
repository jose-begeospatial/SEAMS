import os
import random
import cv2
import subprocess 
import tempfile
from urllib.parse import urlparse
from urllib.request import urlopen



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



