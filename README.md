# ColonyLifeSim

A Colony Life Simulation in python2.7 and pygame

## Table of contents

<!--ts-->
   * [Purpose](#purpose)
   * [Installation](#installation)
      * [Linux](#linux)
      * [Windows](#windows)
   * [Usage](#usage)
      * [Linux](#linux)
      * [Windows](#windows)
   * [How it works](#how-it-works)
      * [Map Generation](#map-generation)
      * [Entities and Behaviours](#entities-and-behaviours)
<!--te-->

## Purpose

TODO

## Installation

Download the project's source code :

![Git download image](https://www.infragistics.com/community/cfs-filesystemfile/__key/CommunityServer.Blogs.Components.WeblogFiles/dhananjay_5F00_kumar.visualstudiogithib/0285.img3.png)

Or clone it using `git clone [this_repo_adress]`. 
If you want to use git, you have to install it first :
* Windows : download it [here](https://git-scm.com/downloads)
* Linux : use `apt-get install git`

### Linux

#### Using pipenv ([link](https://github.com/pypa/pipenv)) (recommended)

Install pipenv is not installed, using 
```sh
pip install pipenv
```

Run, in the project's root directory :
```sh
pipenv install --dev
```

#### Classic

Install the required libs with :
```sh
pip install -r requirements.txt
```

Required libs (see [requirements](./requirements.txt)):
* pygame (1.9.3)
* numpy (1.11.0)
* screeninfo (0.3)

### Windows

#### Python

Download Python2.7 from this [link](https://www.python.org/download/releases/2.7/).

Install Python2.7 by executing the .exe file.

#### Pygame

Download the pygame installer corresponding to Python 2.7 and your OS version from [here](https://www.pygame.org/download.shtml).

Install the .msi (or .exe) file.

#### Other libs

Open the Windows command prompt (cmd).

For __Numpy__ and __screeninfo__, use the pip installer :

```sh
PYTHON_INSTALL_DIR\PATH\python.exe -m pip install numpy
PYTHON_INSTALL_DIR\PATH\python.exe -m pip install screeninfo
```

You might have to update your pip before hand, by doing :

```sh
PYTHON_INSTALL_DIR\PATH\python.exe -m pip install --upgrade pip
```

## Usage

### Linux

#### Using pipenv (recommended)

Run the following, in the project's root directory:

```sh
pipenv shell
python main.py
```

#### Classic

Simply run
`python main.py`
in the project's root directory


### Windows

Locate the Python2.7 installation directory (usually in C:/Python27). 

To run python, open the command prompt and run :

```sh
PYTHON_INSTALL_DIR\PATH\python.exe COLONY_DIR_PATH\main.py
```

You may also use Python IDE, IDLE, to run the project, but as I don't use it, I can't advice you on how to use it.

## How it works

### Map generation

TODO

### Entities and Behaviours

TODO
