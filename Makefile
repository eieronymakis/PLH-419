all:
	sudo docker compose up -d
stop:
	sudo docker compose stop
bash:
	sudo docker exec -it ${id} /bin/bash
db:
	sudo docker exec -i ${id} mysql -uroot -pxyz123 authentication_db < ./backup.sql
restart:
	sudo docker restart ${id}
nginx:
	sudo docker exec -it ${id} nginx -s reload
