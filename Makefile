.PHONY: build clean start stop remove_images
default: start

start:
	docker-compose up -d

stop:
	docker-compose stop && docker-compose rm -f

# build images from Dockerfiles
build:
	docker build -t navi7/harpc -f Dockerfile.harpc .

# remove built images
remove_images:
	docker rmi navi7/harpc

# remove stopped containers
clean:
	docker rm `docker ps -a | grep harpc | awk -- { print $3 }`
