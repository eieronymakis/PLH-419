all:
	sudo docker compose up -d
stop:
	sudo docker compose down
eject:
	sudo docker compose down -v