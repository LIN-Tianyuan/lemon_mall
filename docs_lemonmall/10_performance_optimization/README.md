# 10. Performance optimization
## 10.1 Page Staticization
### 10.1.1 Home page advertisement page static
 - The results of dynamically rendered generated pages are saved as html files and put into a static file server.
 - Users go directly to the static server and access the processed static html files.
```python
# contents/crons.py
def generate_static_index_html():
    """Static Home Page"""
    # Query data on the home page
    categories = get_categories()

    # Check homepage advertisement data
    # Check all advertisement categories
    contents = OrderedDict()
    content_categories = ContentCategory.objects.all()
    for content_category in content_categories:
        contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')   # Check out and sort the unlisted ads

    # Use the advertisement category to find out the content of all advertisements corresponding to the category.

    # Construct context
    context = {
        'categories': categories,
        'contents': contents
    }

    # Render Templates
    # Get the template file first
    template = loader.get_template('index.html')
    # Then render the template file using the context
    html_text = template.render(context)
    # Write template files to static paths
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
```
```bash
python manage.py shell
>>> from contents.crons import generate_static_index_html
>>> generate_static_index_html()
```
```bash
cd ~/lemon_mall/lemon_mall/lemonmall
python -m http.server 8080 --bind 127.0.0.1
```
 - Timed task
```bash
pip3 install django-crontab
```
```python
# settings/dev.py
INSTALLED_APPS = [    
    'django_crontab', # timed task
]

CRONJOBS = [
    # Generate homepage static files every 1 minute
    ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>> ' + os.path.join(os.path.dirname(BASE_DIR), 'logs/crontab.log'))
]

CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'
```
```bash
# Add timed tasks to the system
$ python manage.py crontab add

# crontab: no crontab for citron
# adding cronjob: (afe82496b5176d7774b91d3a15136d68) -> ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>> /Users/citron/Documents/GitHub/lemon_mall/lemon_mall/logs/crontab.log')

# Show activated timed tasks
$ python manage.py crontab show

# Remove Timed Tasks
$ python manage.py crontab remove
```
### 10.1.2 Product details page static
 - Define batch static detail page script files
```python
#!/usr/bin/env python

import sys
sys.path.insert(0, '../')

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

import django
django.setup()

from django.template import loader
from django.conf import settings

from goods import models
from contents.utils import get_categories
from goods.utils import get_breadcrumb


def generate_static_sku_detail_html(sku_id):
    ...
```
 - Execute batch static detail page script file
```bash
chmod +x regenerate_detail_html.py
```
```bash
cd ~/lemon_mall/lemon_mall/script
./regenerate_detail_html.py
# python regenerate_detail_html.py
```
```bash
cd ~/lemon_mall/lemon_mall/lemon_mall
python -m http.server 8080 --bind 127.0.0.1
```

## 10.2 MySQL Read/Write Separation
### 10.2.1 MySQL Master-Slave Synchronization
 - Get a MySQL Image and specifying a MySQL Slave Profile
```bash
sudo docker image pull mysql:8.0

cd ~
mkdir mysql_slave
cd mysql_slave
mkdir data
cp -r /etc/mysql/mysql.conf.d ./
```
 - Modify MySQL Slave Configuration Files
```bash
# ~/mysql_slave/mysql.conf.d/mysqld.cnf
port = 8306
# close log
general_log = 0
# slave number
server-id = 2
```
 - Docker Installation to Run MySQL Slaves
```bash
sudo docker run --name mysql-slave -e MYSQL_ROOT_PASSWORD=mysql -d --network=host   -v /home/lin/mysql_slave/data:/var/lib/mysql   -v /home/lin/mysql_slave/mysql.conf.d/mysqld.cnf:/etc/mysql/my.cnf   mysql:8.0
```
 - Test if the slave was created successfully
```bash
mysql -uroot -pmysql -h 127.0.0.1 --port=8306
```
 - Slave backs up original data of the host
```bash
# Collect original data from the mainframe
mysqldump -uroot -pmysql --all-databases --lock-all-tables > ~/master_db.sql

# The slave copies the original data of the master
mysql -uroot -pmysql -h127.0.0.1 --port=8306 < ~/master_db.sql
```
 - Create an account for synchronizing data from the server
```bash
# Mysql 5.7
# Log in to the host
mysql –uroot –pmysql
# Create a Slave Account
GRANT REPLICATION SLAVE ON *.* TO 'slave'@'%' identified by 'slave';
# Refresh access
FLUSH PRIVILEGES;

# Mysql 8.0
CREATE USER 'slave'@'%' IDENTIFIED BY 'slave_StrongP@ssw0rd123!';
GRANT REPLICATION SLAVE ON *.* TO 'slave'@'%';
```
 - Show binary log messages for MySQL hosts in ubuntu
```bash
SHOW MASTER STATUS;

# Delete the master information file on the slave:
# RESET SLAVE ALL;
```
 - MySQL slave in Docker connecting to MySQL host in ubuntu
```bash
# Mysql 5.7 / 8.0
# Login to Slave
mysql -uroot -pmysql -h 127.0.0.1 --port=8306
# Connect slave to master
change master to master_host='127.0.0.1', master_user='slave', master_password='slave',master_log_file='mysql-bin.000250', master_log_pos=990250;
# Start the slave service
$ start slave;
# Show slave status
$ show slave status \G

# Mysql 8.0+
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='127.0.0.1',
    SOURCE_USER='slave',
    SOURCE_PASSWORD='slave_StrongP@ssw0rd123!',
    SOURCE_LOG_FILE='binlog.000030',
    SOURCE_LOG_POS=1844;
    
STOP REPLICATION;
START REPLICATION;
```
### 10.2.2 Django implementation of MySQL read-write separation
```python
DATABASES = {
    'default': {    # Write(Master)
        'ENGINE': 'django.db.backends.mysql',
        'HOST': IP_ADDRESS,
        'PORT': 3306,
        'USER': 'alex',
        'PASSWORD': '123456abcdefg',
        'NAME': 'lemonmall'
    },
    'slave': {      # Read(Slave)
        'ENGINE': 'django.db.backends.mysql',
        'HOST': IP_ADDRESS,
        'PORT': 8306,
        'USER': 'root',
        'PASSWORD': 'mysql',
        'NAME': 'lemonmall'
    }
}

DATABASE_ROUTERS = ['lemon_mall.utils.db_router.MasterSlaveDBRouter']
```
```python
# lemonmall/utils/db_router.py
class MasterSlaveDBRouter(object):
    """Database read and write routing"""

    def db_for_read(self, model, **hints):
        """Read"""
        return "slave"

    def db_for_write(self, model, **hints):
        """Write"""
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """Whether to run a correlation operation"""
        return True
```
