.PHONY: image server

image:
	docker pull postgres:9.6

server:
	docker run --name postgres -e POSTGRES_PASSWORD=secretpass -d -p 5432:5432 postgres:9.6
