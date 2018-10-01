# Launching a Docker Instance
Before executing this, read about docker [here](https://docs.docker.com/get-started/part1).

Follow these steps to start a docker container:
1. change the ownership of `dockerExec.sh` to root, and make it executable:
```bash
chown root dockerExec.sh
chmod 755 dockerExec.sh
```
2. build an instance through: `docker build -t pace .`:
3. This container will not work without a mariadb container. To set one up, run the following:
```bash
#If you don't have a mariadb image yet, run this as well:
docker pull mariadb

#Now onto making a container:
docker run --name pacedb -d -e MYSQL_ROOT_PASSWORD=1234 -e MYSQL_DATABASE=pace mariadb

#You can now create your conatiner through the following command:
docker run --name nameOfPaceContainer -p 80:80 -d --link pacedb:mysql pace
#This automatically starts the container afterwards.
#From now on, you can start and stop the container by running "docker start nameOfPaceContainer" and "docker stop nameOfPaceContainer" respectively.
```

**Note!** Your new pace instance only works when your database container is also on. Therefore the pace container always runs second when starting everything up.
4. inside your pace-upload script, change the url variable to `http://localhost/upload`
5. In your container, create the path `/pace/prod/portal/upload` if not already created