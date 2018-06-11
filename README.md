# ColonyLifeSim

A Colony Life Simulation in python2.7 and pygame

## Purpose:

TODO

## Installation :

Download the project's source code or clone it using `git clone`.

![Git download image](https://www.infragistics.com/community/cfs-filesystemfile/__key/CommunityServer.Blogs.Components.WeblogFiles/dhananjay_5F00_kumar.visualstudiogithib/0285.img3.png)

To download git :
* Windows : [here](https://git-scm.com/downloads)
* Linux : `apt-get install git`

### Linux :

#### Classic :

Install the required libs with :
`pip install -r requirements.tx`

Required libs (see [requirements](./requirements.txt)):
* pygame (1.9.3)
* numpy (1.11.0)
* screeninfo (0.3)

#### Using pipenv ([link](https://github.com/pypa/pipenv)):

Install pipenv is not installed using `pip install pipenv`

Run `pipenv install --dev`

### Windows :

#### Python :

Download Python2.7 from this [link](https://www.python.org/download/releases/2.7/).

Install Python2.7 by executing the .exe file.

#### Pygame :

Download the pygame installer corresponding to Python 2.7 and your OS version from [here](https://www.pygame.org/download.shtml).

Install the .msi (or .exe) file.

#### Other libs :

Open the Windows command prompt (cmd).

For __Numpy__ and __screeninfo__, use the pip installer :

```sh
PYTHON_INSTALL_DIR\PATH\python.exe -m pip install numpy
PYTHON_INSTALL_DIR\PATH\python.exe -m pip install screeninfo
```

You might have to update your pip before hand, by doing :

`PYTHON_INSTALL_DIR\PATH\python.exe -m pip install --upgrade pip`

## Usage :

### Linux :

#### Classic :

Simply run
`python main.py`
in the main directory

#### Using pipenv :

Run the following :

```sh
pipenv shell
python main.py
```

### Windows :

Locate the Python2.7 installation directory (usually in C:/Python27). 

To run python, open the command prompt and run :

`PYTHON_INSTALL_DIR\PATH\python.exe COLONY_DIR_PATH\main.py`
