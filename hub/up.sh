
# check to see if docker is installed and correct version
DOCKER_VER= docker version --format '{{.Client.Version}}'
echo "Docker version ${DOCKER_VER}"
# TODO: include a version check here

# use docker compose to bring up the environment
docker-compose -p clingenhub -f ./build/docker-compose.yml up -d

# attach to the applicaiton instance
docker attach clingenhub_app_1

# create a network if this does not exist
#if ! docker network ls | grep -q beacon; then
#docker network create beacon
#fi
#docker run -d --net beacon --net-alias mongo --name beaconmongo mongo:3.3.6
#docker run -it --net beacon --name beaconserver -p 5000:80 -v `pwd`/src:/app -v `cd ../sampledata; pwd`:/data -w /app python:3.5.1 bash
