# SEAMS- SEafloor Annotation Module Support

## build seams-app

`docker build -t seams-app  -f Dockerfile.seams .`

## Run docker container

`docker run -it -p 8501:8501 -v ~/develop/SEAMS/seams:/home/user/seams/ seams-app streamlit run ./seams/app.py`
