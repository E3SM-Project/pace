FROM python:2.7-slim

WORKDIR /pace
#COPY . /pace
COPY ./docker/pipRequirements.txt /pace/docker/
RUN apt update && apt-get -y install gcc
RUN pip install --trusted-host pypi.python.org -r docker/pipRequirements.txt

EXPOSE 80
ENV PACE_DOCKER_INSTANCE=1
ENV PACE_RC_DEFAULTS="root 1234 pace pacedb minioftw 12345678 paceminio:9000"

#If you want a developer enviroment, uncomment these commands:
ENV PACE_DEV=1
# RUN apt-get -y install git vim openssh-server
# RUN ["bash","docker/devUserAdd.sh"]
# RUN addgroup paceteam && usermod -aG paceteam root && usermod -aG paceteam devuser
# RUN chmod 775 -R /pace && chown root:paceteam -R /pace
# RUN chmod 775 -R /pace/.git && chown root:paceteam -R /pace/.git
#end dev-env

#If you don't need git, uncomment this:
#RUN rm -rf /pace/.git

#Run!
ENTRYPOINT docker/dockerExec.sh
CMD docker/dockerExec.sh
