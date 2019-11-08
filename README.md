# Luckytruck_backend_solulab
To run backend follow these steps.
->Get clone from https://github.com/LuckyTruckers/Luckytruck_backend_solulab.git
->Remove node modules from it if it is in project folder
->Run npm install
->Download mongoDB if it is not there in your system
->Download xampp to run sql server
->After downloading xampp in that add 3306 port and run sql and apache server.
->After that you can access database from phpMyAdmin e.g. you have to open url of your port number with phpmyadmin 

----After completing above steps do these following steps------
->Open one terminal and run mongod command e.g. if you have installed mongoDB in C drive just open that drive in terminal and run this command rather running that command in any particular folder
->open another terminal in your project folder and run npm start to run your backend.


Note:- 
->Previous backend developer has used mongoDB but any data is not being stored in that everything is stored in sql but to run project we have to run mongoDB also.
->To add/delete/update anything in database you have to run migration. You will able to see one migration folder get reference from that.
->On this URL you will get Express if your project gets run successfully. http://localhost:3000/api
->If npm install doesn't work run sudo npm install.
->These all steps are for local project URL will be changed according to server I mean if you run it from AWS.


