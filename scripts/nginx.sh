
# !/usr/bin/bash

sudo systemctl daemon-reload
sudo rm -f /etc/nginx/sites-enabled/default

sudo cp /home/ubuntu/fd_backend/nginx/nginx.conf /etc/nginx/sites-available/frauddetectionbackend
sudo ln -s /etc/nginx/sites-available/frauddetectionbackend /etc/nginx/sites-enabled/
#sudo ln -s /etc/nginx/sites-available/frauddetectionbackend /etc/nginx/sites-enabled
#sudo nginx -t
#netstat -tnlp | grep -w 80
#netstat -ano|grep 80|grep LISTEN
#sudo netstat -lnp
#sudo lsof -i :80
#netstat -tulpn
#grep -rnw /etc/nginx/ -e '80'

#sudo fuser -k 80/tcp
sudo gpasswd -a www-data ubuntu
sudo systemctl restart nginx

