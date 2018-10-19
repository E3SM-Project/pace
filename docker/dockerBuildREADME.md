# Launching a Docker Instance
Before executing this, read about docker [here](https://docs.docker.com/get-started/part1).

Follow these steps to start a docker container:

1. build an instance through: `docker build -t pace .`:
2. This container will not work without a mariadb or minio container. To set them up, run the following:
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
#The -v flags are optional if this instance is temporary; it links paths on the host system to ones in the container. Therefore, if you don't use these flags, any data after delection of a container will be lost.
```

3. (optional) create a bind-mount to store your .pacerc file. This will sync across the host machine, so the configuration can be changed, or even synced across multiple containers. You can otherwise setup your pacerc file when first running the instance.
```bash
#You can now create your conatiner through the following command:
docker run --name nameOfPaceContainer -p 80:80 -d --link pacedb:mysql -v /path/to/rcdir:/pace/docker/rc --link paceminio:minio/minio pace
#This automatically starts the container afterwards.
#From now on, you can start and stop the container by running "docker start nameOfPaceContainer" and "docker stop nameOfPaceContainer" respectively.

#The following database information is required: database user,user's passowrd, name of target database, database address (if it's another container, it's the name of that container instead of an address.)
#Defaults for database information: root,1234,pace,pacedb

#Defaults for the minio information: minioftw,12345678,paceminio

#Omitting the "-v" argument (or not providing a .pacerc file inside the docker/rc directory) lets you use the above command to insert the pacerc info as arguments. By default it will automatically fill in pre-defined names.
```

**Note!** Your new pace instance only works when your database container is also on. Therefore the pace container always runs second when starting everything up.

4. inside your pace-upload script, change the url variable to `http://localhost/upload`
5. In your container, create the path `/pace/prod/portal/upload` if not already created
