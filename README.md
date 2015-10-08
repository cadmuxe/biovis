Fixing TIM
======

BioVis Contest 2013

3-D renderer switch to Pymol from PyMOL.

Demo
---------
 * [IEEE BioVis 2013 Main Tool Example](https://vimeo.com/97869977)
 * [IEEE BioVis 2013 3D Motion Example](https://vimeo.com/97869975)
 * [IEEE BioVis 2013 Interactive Trend Image Example](https://vimeo.com/97869976)

Dependence
---------
* Pymol 1.6
* PySide
* PyOpenGL
* MySQLdb


System Requirements
-----
Ubuntu 12.04 and up

If using either Macintosh or Windows:
* Download Virtual Box (https://www.virtualbox.org/), or any equivalent piece of software (Parallels Desktop, VMWare, etc.)
* Download Ubuntu Desktop (http://www.ubuntu.com/download), making sure it is version 12.04 or newer
* Follow the instructions (https://www.virtualbox.org/manual/ch02.html) to setup the virtual machine

Installation
------------

* Download the code by either:
	*  git clone https://github.com/cadmuxe/biovis .
	* Downloading the zip: https://github.com/cadmuxe/biovis/archive/master.zip

* From Ubuntu, launch a terminal window
* Execute the following commands in the terminal window (copy and paste):
	* sudo apt-get update 
	* sudo apt-get install build-essential python2.7 freeglut3 libgl1-mesa-glx libglu1-mesa python-tk python-pmw python-pip python2.7-dev python-pyside mysql-client python-mysqldb pymol cmake qt4-default python-qt4* git
	* sudo pip install --upgrade pip
	* sudo pip install numpy pyopengl 
* change to the fixingTIM directory and run: python ./qt.py
