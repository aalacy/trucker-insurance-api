#!/usr/bin/env bash

# some other niceties could be found here:
# https://www.snip2code.com/Snippet/16602/Vagrant-provision-script-for-php--Apache

# update / upgrade
sudo apt update
sudo apt -y upgrade


# install MySQL
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo apt -y install vim htop mc unzip git curl npm

sudo apt -y autoremove

sudo apt clean

#cp /var/www/nosweat/rename_me_to_config.js /var/www/nosweat/config.js

#mongo db
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
sudo apt-get update
sudo apt-get install -y mongodb-org

echo "Setting up default settings"
rm -rf /var/lib/mongodb/*
cat > /etc/mongod.conf <<'EOF'
 storage:
   dbPath: /var/lib/mongodb
   directoryPerDB: true
   journal:
     enabled: true
   engine: "wiredTiger"

 systemLog:
   destination: file
   logAppend: true
   path: /var/log/mongodb/mongod.log

 net:
   port: 27017
   bindIp: 0.0.0.0
   maxIncomingConnections: 100

 replication:
   oplogSizeMB: 128
   replSetName: "rs1"

 security:
   authorization: enabled

EOF

sudo service mongod start
sleep 5

mongo admin <<'EOF'
use admin
rs.initiate()
exit
EOF

sleep 5

echo "Adding admin user"
mongo admin <<'EOF'
use admin
rs.initiate()
var user = {
  "user" : "admin",
  "pwd" : "1q2w3e4r5t6y",
  roles : [
      {
          "role" : "userAdminAnyDatabase",
          "db" : "admin"
      }
  ]
}
db.createUser(user);
exit
EOF

sudo service mongod start

mongo admin -u admin -p 1q2w3e4r5t6y <<'EOF'

use luckytrack
db.createUser(
  {
   user: "luckytrackUser",
   pwd: "1q2w3e4r5t6y",
   roles: [ "readWrite"]
  })
exit
EOF

#mongo nosweat -u nosweatUser -p s233kaar <<'EOF'
#
#db.adminusers.save({email:'aaa@aaa.com', password: 'aaa'})
#
#exit
#EOF

cd /var/www/html/
npm install
sudo npm install -g nodemon
sudo apt-get install imagemagick -y
## DEBUG=nosweat:* & npm run devstart

sudo npm install mocha -g
sudo npm install -g n
sudo n latest
sudo apt install -y mc

sudo echo "mysql-server mysql-server/root_password password 1q2w3e4r777y" | debconf-set-selections
sudo echo "mysql-server mysql-server/root_password_again password 1q2w3e4r777y" | debconf-set-selections
sudo apt -y install mysql-server

mysql -u root -p1q2w3e4r777y -e "CREATE DATABASE luckytruck;";