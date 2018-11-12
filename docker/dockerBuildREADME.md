# Launching a Docker Instance
Before executing this, read about docker [here](https://docs.docker.com/get-started/part1).

Follow these steps to start a docker container:

**Pre-made folders should already be available for logging (`/pace/assets/static/logs`), and uploads to raw data (`/pace/prod/portal/upload`). If they do not exist, create these now before building the container.**

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

3. (optional) create a bind-mount to store your .pacerc file. This will sync across the host machine, so the configuration can be changed, or even synced across multiple containers.   
    * *Omitting this step (or if the bind-mount is empty) lets you insert everything for the pacerc via arguments in the following command. Omitting the arguments fills the pacerc in with a default configuration.*
        * Defaults for database information: root,1234,pace,pacedb
        * Defaults for the minio information: minioftw,12345678,paceminio
4. Create your conatiner through the following command:
```bash
docker run --name nameOfPaceContainer -p 80:80 -d --link pacedb:mysql -v /path/to/rcdir:/pace/docker/rc --link paceminio:minio/minio pace
```

5. inside your pace-upload script, change the url variable to `http://localhost/upload`
6. To upload new experiments, a Github account is required. Log into your mariadb instance (`docker exec -it dbContainerName mysql -p pace`), and add yourself (and potential others) to the `authusers` table:
```sql
insert into authusers values(null,"yourUsernameHere");
```

## Notes
* From now on, you can start and stop the container by running "docker start nameOfPaceContainer" and "docker stop nameOfPaceContainer" respectively.
* Your new pace instance only works when your database & mariadb containers are also on. Therefore the pace container always runs last when starting everything up.