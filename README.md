![image](https://img.shields.io/badge/MySQL-005C84?style=for-the-badge&logo=mysql&logoColor=white)
![image](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![image](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![image](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![image](https://img.shields.io/badge/Apache-D22128?style=for-the-badge&logo=Apache&logoColor=white)
![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)

# *PLH-419*
# MapReduce System Project

# *Setup Guide*


*1. Run `sudo docker compose up` in the project folder* <br>
*2. Find the database container id and run `make db id={database_cont_id}`* <br>
*3. Run `sudo docker restart`* <br>
*4. Run `bash network.bash`, get the IP's of Monitoring and UI Service Replicas and update the NGINX configuration files* <br>
*5. Run `nginx -r reload` inside each NGINX container* <br>
*6. Done*


# *Service Diagram Docker*
![alt text](https://github.com/git-egi/PLH-419/blob/main/service_diagram_docker.drawio.png?raw=true)
