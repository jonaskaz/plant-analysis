# Basic Storage API

Storage API that recieves images and stores them in a directory. For example usage of this API please view the storage_test.py file.

Build the docker container:
```
docker build -t jonaskaz/comprobo-storage-api .
```
Push the docker image with the tag latest:
```
docker push jonaskaz/comprobo-storage-api:latest
```

Docker login setup:
https://leimao.github.io/blog/Docker-Login-Encrypted-Credentials/


Ping the ansible hosts:
```
ansible -i hosts all -m ping
```
Check the ansible playbook:
```
ansible-playbook -i hosts deploy.yml --check
```
Deploy the latest docker image:
```
ansible-playbook -i hosts deploy.yml
```
Get access to a the container:
```
docker exec -it comprobo-storage-api /bin/bash
```

