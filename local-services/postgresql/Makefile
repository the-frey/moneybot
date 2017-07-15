.PHONY: image server

image:
	docker build -t postgres:moneybot .

server:
	docker run -d -p 5432:5432 --name=postgres postges:moneybot
