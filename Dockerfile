FROM electronifie/docker-scientific-python:latest
MAINTAINER Ian McAllister "https://github.com/imcallister/savorifie"

ENV USERID 5000

RUN groupadd -g $USERID accountifie
RUN useradd -u $USERID -g accountifie accountifie

RUN mkdir /efie-accountifie
WORKDIR /efie-accountifie

ADD docker_requirements.txt /savorifie-accountifie/

RUN pip install -r docker_requirements.txt


RUN ls
ADD . /savorifie/
RUN npm install accountifie-svc -g

