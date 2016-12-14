# Arestor - Quickstart

[![Build Status](https://travis-ci.org/alexcoman/arestor.svg?branch=master)](https://travis-ci.org/alexcoman/arestor)


You first need to install Arestor. This is done with pip after you check out the Arestor repo:
```bash
~ $ sudo apt-get install redis-server vim git python-dev -y
~ $ git clone https://github.com/alexcoman/arestor
~ $ cd arestor
~ $ git checkout feature/resource-management
~ $ pip install virtualenv
~ $ virtualenv .venv/arestor
~ $ source .venv/arestor/bin/activate
~ $ pip install ../arestor
~ $ python setup.py install
~ $ oslo-config-generator --config-file etc/arestor/arestor-config-generator.conf
~ $ mkdir /etc/arestor/
~ $ cp etc/arestor/arestor.conf.sample /etc/arestor/arestor.conf
```

Running Arestor: 
```bash
~ $ arestor server start # To start running the Arestor server

```

## Notes
### On Windows you will need to install these dependencies, in order for the Arestor installation to be successful: 
* http://aka.ms/vcpython27
* https://github.com/MSOpenTech/redis/releases

### Make sure the `arestor.conf` file has been modified properly before trying to run Arestor, otherwise it will run with the default values.