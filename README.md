# Blogy application

A blog post app for our life

## Getting started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 
See deployment for notes on how to deploy the project on a live system.

### Prerequisites

To running this app, you will need to install the following software:

```
python 3.6+
pip 19.1.1
virtualenv
MySQL 5.7.20+
```

### Installing

This project is configured for MySQL running at localhost, so if you're running
MySQL in another host, please change the MySQL url in `config.py` file.

Create MySQL database and user:

```mysql
CREATE DATABASE blogy CHARACTER SET utf8mb4;

CREATE USER 'blogger'@'%' IDENTIFIED BY 'abcd#1234';

GRANT ALL PRIVILEGES ON blogy.* TO 'blogger'@'%';
```

If you are not installed `virtualenv` then installing it now:

```shell script
$ pip install virtualenv
```

Then, go to the app directory after cloning it on github:

```shell script
$ cd blogy/

$ virtualenv venv

$ source venv/bin/activate
```

If you're intended to running development then run this command
```shell script
$ pip install -r requirements/dev.txt
```
Otherwise, run this command to install production dependencies
```shell script
$ pip install -r requirements/prod.txt
```

### Running the development environment

Activating the virtual environment
```shell script
$ source venv/bin/activate
```

Exporting theses two variables in shell:
```shell script
$ export FLASK_APP=main.py
$ export FLASK_DEBUG=1
```

Then run it using:
```shell script
$ flask run
```

