# Launching a Docker Instance
Before executing this, read about docker [here](https://docs.docker.com/get-started/part1).

Follow these steps to start a docker container:
1. change the ownership of `dockerExec.sh` to root, and make it executable:
```bash
chown root dockerExec.sh
chmod 755 dockerExec.sh
```
2. build an instance through: `docker build -t pace .`:
3. This container will not work without a mariadb or minio container. To set them up, run the following:
```bash
#Run these if you don't have them yet:
#docker
docker pull mariadb
#minio
docker pull minio/minio

#Now onto making a container:
#Launch a maria db instance:
docker run --name pacedb -d -e MYSQL_ROOT_PASSWORD=1234 -e MYSQL_DATABASE=pace mariadb
#Launch a minio instance:
docker run --name paceminio -e MINIO_ACCESS_KEY=accessKey -e MINIO_SECRET_KEY=secretKey -v /path/to/config:/root/.minio -v /path/to/data:/data minio/minio server /data

#You can now create your conatiner through the following command:
docker run --name nameOfPaceContainer -p 80:80 -d --link pacedb:mysql --link paceminio:minio/minio -e PACE_DOCKER_DB_INFO="root,dbPasswordHere,dbNameHere,dbAddressHere" -e PACE_MINIO_INFO="accessKey,secretKey,url" pace
#This automatically starts the container afterwards.
#From now on, you can start and stop the container by running "docker start nameOfPaceContainer" and "docker stop nameOfPaceContainer" respectively.

#PACE_DOCKER_DB_INFO specifies the following attributes (in order): database user,user's passowrd, name of target database, database address (if it's another container, it's the name of that container instead of an address.)
#Defaults for PACE_DOCKER_DB_INFO: root,1234,pace,pacedb

#Defaults for the minio information: minioftw,12345678,paceminio
```

**Note!** Your new pace instance only works when your database container is also on. Therefore the pace container always runs second when starting everything up.

4. inside your pace-upload script, change the url variable to `http://localhost/upload`
5. In your container, create the path `/pace/prod/portal/upload` if not already created
