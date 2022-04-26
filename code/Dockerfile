# define the base image
FROM python:3.10.4-slim

#allows for log messages to be immediately dumped to the stream instead of being buffered
ENV PYTHONBUFFERED 1

#Create base directory
RUN mkdir /code

#Define working directory
WORKDIR /code

#add all the cuuret content to working directory
ADD . /code/

#Install all dependencies
RUN pip install -r ./requirements.txt

#Its optinal if we want to run the script by defult or it better to handel in the docker-compose file
#CMD [ "python", "-u", "./main.py" ]

