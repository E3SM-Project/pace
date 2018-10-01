FROM python:2.7-slim

WORKDIR /pace
COPY . /pace
RUN apt update && apt-get -y install gcc
RUN pip install --trusted-host pypi.python.org -r pipRequirements.txt

EXPOSE 80
ENV PACE_DOCKER_INSTANCE=1
ENV PACE_DOCKER_DB_INFO="root,1234,pace,pacedb"

CMD "./dockerExec.sh"