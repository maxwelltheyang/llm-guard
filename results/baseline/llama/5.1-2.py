version: '3'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - db
    environment:
      - USER=myuser
      - GROUP=mygroup
    user: myuser
    working_dir: /app

volumes:
  app_data:
    driver: local

networks:
  default:
    external:
      name: app_net

container_user:
  uid: 1000
  gid: 1001
