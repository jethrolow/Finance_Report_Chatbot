FROM continuumio/miniconda3 AS build

#update and install required packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
RUN conda update -n base -c defaults conda

# specify the working directory
WORKDIR /app

# run gitclone to copy in the latest code from Github
RUN git clone https://github.com/streamlit/streamlit-example.git .

# create the conda environment using the environment.yaml file
RUN conda env create -f 

#expose port for access
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]