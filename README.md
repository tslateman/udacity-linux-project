# udacity-linux-project

Project purpose is to setup a linux server and configure it to run the item catalog app from a previous project. 

Files in the repo are placed in /var/www/

Below is the catalogApp.conf file in /etc/apache2/sites-available/

<VirtualHost *:80>
                ServerName 52.32.167.246
                ServerAlias ec2-52-32-167-246.us-west-2-compute.amazonaws.com
                ServerAdmin t.r.slater@gmail.com
                WSGIScriptAlias / /var/www/catalog.wsgi
                <Directory /var/www/ItemCatalogApp/>
                        Order allow,deny
                        Allow from all
                </Directory>
                Alias /static /var/www/ItemCatalogApp/static
                <Directory /var/www/ItemCatalogApp/static/>
                        Order allow,deny
                        Allow from all
                </Directory>
                ErrorLog ${APACHE_LOG_DIR}/error.log
                LogLevel warn
                CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
