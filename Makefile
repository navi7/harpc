.PHONY: build clean start stop remove_images shell rabbit_tracing
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

# enter a running container
shell:
	docker exec -it harpc_service_product_1 bash -c 'source bin/activate && bash'

# enable tracing plugin in RabbitMQ
rabbit_tracing:
	docker exec -i harpc_rpc_queue_1 rabbitmq-plugins enable rabbitmq_tracing
