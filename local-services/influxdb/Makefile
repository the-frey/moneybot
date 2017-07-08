.PHONY: image server

image:
	docker build -t influxdb:moneybot .

server:
	docker run -d -p 8086:8086 --name=influxdb influxdb:moneybot
