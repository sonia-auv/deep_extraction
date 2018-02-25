# deep-learning

# Installation

## Ubuntu 16.04.03

We must first install python 3.6 

```bash 
$ sudo add-apt-repository ppa:jonathonf/python-3.6
$ sudo apt-get update
$ sudo apt-get install -y python3.6 python3.6-dev 
``` 

### Install virtualenv 

```bash 
$ sudo apt-get install -y python-pip
$ sudo pip install virtualenv 
$ sudo pip install virtualenvwrapper
```

### Install virtualenvwrapper

Create required folder to store your virtualenv and your project

```bash
$ mkdir $HOME/.virtualenvs
$ mkdir $HOME/Projects
```

Insert those line at the bottom of your shell config file i.e: .bashrc

```bash
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/Projects
source /usr/local/bin/virtualenvwrapper.sh
```

### Create project virtualenv

This will create a virtualenv for the project 

```bash
$ cd PROJECT_DIR
$ mkvirtualenv -p python3.6 image-augmentation-tool
```

For more information [virtualenvwrapper doc](https://virtualenvwrapper.readthedocs.io/en/latest/)


### Install python requirements

This will install python requierements

```bash 
$ pip install -r requirements.txt 
```