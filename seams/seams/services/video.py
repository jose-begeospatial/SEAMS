import os
import streamlit as st 
from seams.video_tools import get_video_info, extract_frames_every_n_seconds





st.cache_data(show_spinner=True)
def extract_frames(video_filepath):
        
    if video_filepath is not None and os.path.isfile(video_filepath):
        video_info =  get_video_info(video_path=video_filepath)
        st.write(video_info)
        temp_frames = extract_frames_every_n_seconds(
        video_path=video_filepath, 
        output_dir='/home/begeospatial/develop/SEAMS/seams/seams/data',
        n_seconds=5, 
        total_frames=video_info['frame_count'], 
        fps=video_info['fps']
        )

        if temp_frames:
            st.write(temp_frames)
        return temp_frames



def video_player(
    video_path, 
    marker_positions = [100, 200, 500, 850, 1100, 1500, 2000, 3000, 4000]):
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
        """.format(video_path, marker_positions, marker_positions), unsafe_allow_html=True )


# --
# -------------------------------------------------------
video_filepath = st.text_input(
    label='filepath', 
    placeholder='please provide the video filepath')    


if video_filepath:
    #video_player(video_path="/home/begeospatial/develop/dockers/poetry-havsmus/poetry_havsmus/survey_data/raw/media/videos_mp4/nam21.mp4")
    pass

# /home/begeospatial/develop/dockers/poetry-havsmus/poetry_havsmus/survey_data/raw/media/videos_mp4/nam21.mp4
