all:
	sudo docker compose up -d
stop:
	sudo docker compose down
eject:
	sudo docker compose down -v
db:
	sudo docker exec -i ${id} mysql -uroot -pxyz123 auth_svc < ./backup.sql

