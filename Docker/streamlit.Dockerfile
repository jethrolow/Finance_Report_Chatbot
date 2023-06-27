FROM continuumio/miniconda3

#update and install required packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && touch "~/.bashrc"
RUN conda update -n base -c defaults conda

# specify the working directory
WORKDIR /app

# run gitclone to copy in the latest code from Github
RUN git clone https://github.com/jethrolow/Finance_Report_Chatbot.git .

# create the conda environment using the environment.yaml file
RUN conda env create -f conda_environment.yaml && \
    conda init bash && \
    conda clean -a -y && \
    echo "source activate fr_chatbot" >> "~/.bashrc"

#expose port for access
EXPOSE 8501

#check connection
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["/bin/bash", "./entrypoint.sh"]