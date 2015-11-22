# udacity-linux-project

Project purpose is to setup a linux server and configure it to run the item catalog app from a previous project. 

Files in the repo are placed in /var/www/

IP: 52.32.167.246
SSH port: 2200
App: /var/www/ItemCatalogApp/

Setup Steps Summary:

Commands:
adduser grader

Entered password and profile information

To grant sudo:

Command:
visudo

Update the file to include the following:
# User privilege specification
root    ALL=(ALL:ALL) ALL
grader  All=(ALL:ALL) ALL

Commands:
apt-get update
apt-get dist-upgrade

A new version of /boot/grub/menu.lst is available, but the version installed currently has been locally modified.
install the package maintainer's version


Configure the local timezone to UTC

Enter: dpkg-reconfigure tzdata
Select: None of the above
Select: UTC


cp /etc/ssh/sshd_config /etc/ssh/sshd_config_backup
vim /etc/ssh/sshd_config

# What ports, IPs and protocols we listen for
Port 2200

Firewall
Commands:
ufw default deny incoming
ufw default allow outgoing
ufw allow http
ufw allow ntp
ufw allow 2200/tcp

Update file /etc/ssh/sshd_config
Uncomment line with # Port 22
Update to Port 2200

Command: service ssh restart

apt-get install apache2
apt-get install libapache2-mod-wsgi
apt-get install postgresql
apt-get install python-psycopg2
apt-get install python-pip
pip install SQLAlchemy 
pip install postgresql
pip install Flask
pip install oauth2client
pip install flask-seasurf

Configure with apache. Mostly followed digital ocean steps. 
Update paths and references for my version.
Add server IP and amazon ec2 to account for credentials
Saved client secrets file. Reload apache.

I ran into an oauth error that took some back and forth attempts... Mostly a waste. 
Turns out I was missing the amazon ec2 address in my javascript origins. 

Outside Resources:

https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps
http://kracekumar.com/post/71120049966/deploying-full-fledged-flask-app-in-production
https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
install pip

