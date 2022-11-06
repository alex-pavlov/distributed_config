# Distributed config API service

# Description of project and motivation

Реализовать сервис, который позволит динамически управлять конфигурацией приложений. Доступ к сервису должен осуществляться с помощью API. Конфигурация может храниться в любом источнике данных, будь то файл на диске, либо база данных. Для удобства интеграции с сервисом может быть реализована клиентская библиотека.

# Prerequisites & Installation, including code samples for how to download all pre-requisites

Во время работы над этим проектом я использовал:
1. Операционную систему Ubuntu 20.04.1 LTS
2. Python 3.8.10, фреймворк Flask, flask shell, СУБД SQLite, ORM SQlAlchemy и другие модули для Python3 и Flask
3. Локальную разработку производил в  “virtual environment” с помощью модуля venv для Python 3
4. Командную оболочку Bash
5. Редактор vi
6. Тестирование API endpoinds производил с помощью программы командной строки cURL
и фреймворка unittest для Python 3 
7. Для контейнеризации был написан и протестирован Dockerfile

# Local Development, including how to set up the local development environment and run the project locally

Для локального тестирования в директории distributed_config создайте виртуальное окружение с помощью команд:

python3 -m venv virt
source virt/bin/activate
pip3 install -r requirements.txt

Отключить виртуальное окружение можно с помощью команды deactivate

Список установленных в виртуальное окружение модулей Python 3 можно проверить с помощью команды pip3 freeze

Файл приложения называется app.py 
Для запуска приложения в режиме отладки используйте команду flask --debug run
После запуска, приложение выведет в Bash текст:

(virt) alex@alex-pc:~/distributed_config$ flask --debug run
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 136-404-621

Это означает, что приложение работает локально и использует порт 5000: http://127.0.0.1:5000

При этом SQLite автоматически создаст файл базы данных в директории distributed_config/instance

Пример:

(virt) alex@alex-pc:~/distributed_config$ cd instance/
(virt) alex@alex-pc:~/distributed_config/instance$ ls -al
total 24
drwxrwxr-x 2 alex alex  4096 Nov  6 13:34 .
drwxrwxr-x 5 alex alex  4096 Nov  6 13:50 ..
-rw-r--r-- 1 alex alex 16384 Nov  6 13:34 apps_configs.db
(virt) alex@alex-pc:~/distributed_config/instance$ 

На данный момент для работы с API реализован HTTP endpoint /config
с поддержкой методов GET, POST, PATCH, DELETE
Указать название сервиса можно с помощью параметра ?service=
Пример: http://localhost:5000/config?service=managed-k8s
Данные передаются в формате JSON.
Приложение поддерживает все CRUD операции, есть защита от повторного добавления
сервисов с одинаковым названием, поддерживается версионирование при добавлении новых
конфигураций JSON, версиям присваиваются номера начиная с 0
С помощью HTTP метода DELETE, возможно удаление конфигураций, у которых атрибут
enabled имеет значение False, но по умолчанию у всех конфигураций этот атрибут имеет 
значение True и его изменение не доступно через API

Для тестирования приложения используется Python фреймворк unittest
Чтобы запустить тестирование введите в терминале Bash команду python3 app.py

Пример:

(virt) alex@alex-pc:~/distributed_config$ python3 app.py 
..
----------------------------------------------------------------------
Ran 2 tests in 0.036s

OK
(virt) alex@alex-pc:~/distributed_config$ 


Пример работы с API приложения в терминале Bash с помощью программы curl:

alex@alex-pc:~/distributed_config$ ls -al
total 76
drwxrwxr-x  5 alex alex  4096 Nov  6 14:15 .
drwxr-xr-x 38 alex alex  4096 Nov  6 14:15 ..
-rw-rw-r--  1 alex alex 11273 Nov  6 12:16 app.py
-rw-rw-r--  1 alex alex   211 Nov  6 12:26 Dockerfile
drwxrwxr-x  2 alex alex  4096 Nov  6 14:10 instance
-rw-rw-r--  1 alex alex   109 Nov  5 18:38 k8s_data_0.json
-rw-rw-r--  1 alex alex   165 Nov  6 09:58 k8s_data_1.json
-rw-rw-r--  1 alex alex   103 Nov  5 18:43 nginx_data_0.json
-rw-rw-r--  1 alex alex   159 Nov  6 14:15 nginx_data_1.json
drwxrwxr-x  2 alex alex  4096 Nov  6 13:34 __pycache__
-rw-rw-r--  1 alex alex  2472 Nov  6 13:31 README.md
-rw-r--r--  1 alex alex 16384 Nov  6 14:08 .README.md.swp
-rw-rw-r--  1 alex alex   242 Nov  6 02:13 requirements.txt
drwxrwxr-x  6 alex alex  4096 Nov  6 13:32 virt
alex@alex-pc:~/distributed_config$ curl -d "@k8s_data_0.json" -H "Content-Type: application/json" -X POST http://localhost:5000/config?service=managed-k8s
{
  "ID": 1,
  "enabled": true,
  "service": "managed-k8s",
  "serviceJSONconf": "{\"service\": \"managed-k8s\", \"data\": [{\"key1\": \"value1\"}, {\"key2\": \"value2\"}]}",
  "success": true,
  "total_configs": 1
}
alex@alex-pc:~/distributed_config$ curl -d "@nginx_data_0.json" -H "Content-Type: application/json" -X POST http://localhost:5000/config?service=managed-k8s
{
  "error": 422,
  "message": "unprocessable",
  "success": false
}
alex@alex-pc:~/distributed_config$ curl -d "@nginx_data_0.json" -H "Content-Type: application/json" -X POST http://localhost:5000/config?service=nginx
{
  "ID": 2,
  "enabled": true,
  "service": "nginx",
  "serviceJSONconf": "{\"service\": \"nginx\", \"data\": [{\"key1\": \"value1\"}, {\"key2\": \"value2\"}]}",
  "success": true,
  "total_configs": 2
}
alex@alex-pc:~/distributed_config$ curl http://localhost:5000/config?service=managed-k8s
{"service": "managed-k8s", "data": [{"key1": "value1"}, {"key2": "value2"}]}alex@alex-pc:~/distributed_config$ 
alex@alex-pc:~/distributed_config$ curl http://localhost:5000/config?service=nginx
{"service": "nginx", "data": [{"key1": "value1"}, {"key2": "value2"}]}alex@alex-pc:~/distributed_config$ curl http://localhost:5000/config?service=junk
{
  "error": 404,
  "message": "resource not found",
  "success": false
}
alex@alex-pc:~/distributed_config$ curl -d "@k8s_data_1.json" -H "Content-Type: application/json" -X PATCH http://localhost:5000/config?service=managed-k8s
{
  "success": true
}
alex@alex-pc:~/distributed_config$ curl http://localhost:5000/config?service=managed-k8s
{
  "0": "{\"service\": \"managed-k8s\", \"data\": [{\"key1\": \"value1\"}, {\"key2\": \"value2\"}]}",
  "1": "{\"service\": \"managed-k8s\", \"data\": [{\"key1\": \"value1\"}, {\"key2\": \"value2\"}, {\"key3\": \"value3\"}, {\"key4\": \"value4\"}]}"
}
alex@alex-pc:~/distributed_config$ 

# Docker

Чтобы использовать Dockerfile, предварительно установите его, после чего создать контейнер и управлять им можно с помощью команд:

docker build --tag dist_conf .

alex@alex-pc:~/distributed_config$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
dist_conf           latest              e438af34a3a8        2 hours ago         180MB
python              3.8-slim-buster     d55c26ea3903        12 days ago         117MB
alex@alex-pc:~/distributed_config$ docker run -d -p 5000:5000 dist_conf
b1e72d52351f770ba5ed96224d7091376ef155ae2c82c981648830dcf8a870e1
alex@alex-pc:~/distributed_config$ curl -d "@k8s_data_0.json" -H "Content-Type: application/json" -X POST http://localhost:5000/config?service=managed-k8s
{"ID":1,"enabled":true,"service":"managed-k8s","serviceJSONconf":"{\"service\": \"managed-k8s\", \"data\": [{\"key1\": \"value1\"}, {\"key2\": \"value2\"}]}","success":true,"total_configs":1}
alex@alex-pc:~/distributed_config$ docker stop -t 60 dist_conf
Error response from daemon: No such container: dist_conf
alex@alex-pc:~/distributed_config$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
dist_conf           latest              e438af34a3a8        2 hours ago         180MB
python              3.8-slim-buster     d55c26ea3903        12 days ago         117MB
alex@alex-pc:~/distributed_config$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
b1e72d52351f        dist_conf           "python3 -m flask ru…"   2 minutes ago       Up 2 minutes        0.0.0.0:5000->5000/tcp   dazzling_darwin
alex@alex-pc:~/distributed_config$ docker stop b1e72d52351f
b1e72d52351f
alex@alex-pc:~/distributed_config$ curl -d "@k8s_data_0.json" -H "Content-Type: application/json" -X POST http://localhost:5000/config?service=managed-k8s
curl: (7) Failed to connect to localhost port 5000: Connection refused
alex@alex-pc:~/distributed_config$ 

