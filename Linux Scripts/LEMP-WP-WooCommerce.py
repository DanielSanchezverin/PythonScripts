#!/usr/bin/env python3

import argparse, subprocess, fileinput

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', help='Wordpress directory', type=str)
parser.add_argument('-u', '--user', help='WWW-datauser', type=str)
parser.add_argument('-n', '--name', help='Website name', type=str)
parser.add_argument('-U', '--wpuser', help='WordPress admin user', type=str)
parser.add_argument('-P', '--pssw', help='WordPress admin user password', type=str)
parser.add_argument('-e', '--email', help='WordPress admin user email', type=str)
parser.add_argument('-N', '--dbname', help='Database name', type=str)
parser.add_argument('-d', '--dbuser', help='Database user', type=str)
parser.add_argument('-D', '--dbpass', help='Database password', type=str)
args=parser.parse_args()

#Find and replace function
def sar(txtsearch, txtreplace, filesearch):
    with open(filesearch, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace(txtsearch, txtreplace)
    with open(filesearch, 'w') as file:
        file.write(filedata)
    print("Done")

#LEMP installation
#Nginx installation
subprocess.run("sudo apt update", shell=True)
subprocess.run("sudo apt install nginx -y", shell=True)
subprocess.run("sudo ufw allow 'Nginx Full'", shell=True)
#Installation mysql
subprocess.run("sudo apt install mysql-server php-mysql unzip -y", shell=True)
#Php-fpm installation
subprocess.run("sudo apt install php-fpm php-curl php-gd php-intl php-mbstring php-soap php-xml php-xmlrpc php-zip -y", shell=True)

#Wordpress installation
subprocess.run("sudo wget -O wordpress.tar.gz https://wordpress.org/latest.tar.gz", shell=True)
subprocess.run("sudo tar -xzvf wordpress.tar.gz", shell=True)
subprocess.run("sudo mv wordpress " + str(args.path), shell=True)

#Nginx setup with wordpress
subprocess.run("sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/wordpress", shell=True)
sar("/var/www/html", str(args.path), "/etc/nginx/sites-available/wordpress")
sar("server_name _;", "server_name " + str(args.name) + ";", "/etc/nginx/sites-available/wordpress")
sar("index index.html index.htm index.nginx-debian.html;", "index index.php index.html index.htm index.nginx-debian.html;", "/etc/nginx/sites-available/wordpress")
sar("#location ~ \.php$ {", "location ~ \.php$ {", "/etc/nginx/sites-available/wordpress")
subprocess.run("sudo sed -i 's/#.include snippets\/fastcgi-php\.conf;/include snippets\/fastcgi-php\.conf;/g' /etc/nginx/sites-available/wordpress", shell=True)
subprocess.run("sudo sed -i 's/#.fastcgi_pass unix:\/var\/run\/php\/php7\.4-fpm\.sock;/fastcgi_pass unix:\/var\/run\/php\/php7\.4-fpm\.sock;/g' /etc/nginx/sites-available/wordpress", shell=True)
subprocess.run("sudo sed -i '52,72s/#}/}/g' /etc/nginx/sites-available/wordpress", shell=True)
sar("#location ~ /\.ht {", "location ~ /\.ht {", "/etc/nginx/sites-available/wordpress")
subprocess.run("sudo sed -i 's/#.deny all;/deny all;/g' /etc/nginx/sites-available/wordpress", shell=True)
#Enable wordpress
subprocess.run("sudo unlink /etc/nginx/sites-enabled/default", shell=True)
subprocess.run("sudo ln -s /etc/nginx/sites-available/wordpress /etc/nginx/sites-enabled/wordpress", shell=True)

#Mysql configuration
subprocess.run("sudo mysql -e \"CREATE DATABASE " + str(args.dbname) + ";\"", shell=True)
subprocess.run("sudo mysql -e \"CREATE USER '" + str(args.dbuser) + "'@'localhost' IDENTIFIED BY '" + str(args.dbpass) +"';\"", shell=True)
subprocess.run("sudo mysql -e \"GRANT ALL PRIVILEGES ON " + str(args.dbname) + ".* TO '" + str(args.dbuser) + "'@'localhost';\"", shell=True)
subprocess.run("sudo mysql -e \"show databases;\"", shell=True)
subprocess.run("sudo mysql -e \"SELECT user FROM mysql.user;\"", shell=True)

#Phpmyadmin installation
subprocess.run("sudo wget -O phpMyAdmin.zip https://files.phpmyadmin.net/phpMyAdmin/5.1.1/phpMyAdmin-5.1.1-all-languages.zip", shell=True)
subprocess.run("sudo unzip phpMyAdmin.zip -d " + str(args.path) + "/phpMyAdmin", shell=True)

#Installation and configuration of wp-cli
subprocess.run("curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar", shell=True)
subprocess.run("chmod +x wp-cli.phar", shell=True)
subprocess.run("sudo mv wp-cli.phar /usr/local/bin/wp", shell=True)

#User and wp-config configuration
subprocess.run("sudo useradd " + str(args.user), shell=True)
subprocess.run("sudo chown -R " + str(args.user) + ":" + str(args.user) + " " + str(args.path), shell=True)
subprocess.run("sudo chmod -R 777 " + str(args.path) + "/wp-content", shell=True)
subprocess.run("cd " + str(args.path), shell=True)
subprocess.run("sudo -u " + str(args.user) + " wp core config --dbname='" + str(args.dbname) + "' --dbuser='" + str(args.dbuser) + "' --dbpass='" + str(args.dbpass) + "' --dbhost='localhost' --dbprefix='wp_' --path=" + str(args.path) + " --allow-root", shell=True)
subprocess.run("sudo -u " + str(args.user) + " wp core install --url='http://" + str(args.name) + "/' --title='" + str(args.name) + "' --admin_user='" + str(args.wpuser) + "' --admin_password='" + str(args.pssw) + "' --admin_email='" + str(args.email) + "' --path=" + str(args.path) + " --allow-root", shell=True)

#WooCommerce Installation
subprocess.run("sudo wp plugin install woocommerce --path=" + str(args.path) + " --allow-root", shell=True)

#Nginx restart
subprocess.run("sudo systemctl restart nginx.service", shell=True)