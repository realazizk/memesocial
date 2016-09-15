
# memesocial project

[![Build Status](https://travis-ci.org/mohamed-aziz/memesocial.svg?branch=master)](https://travis-ci.org/mohamed-aziz/memesocial)

<p align="center">
	![Thememe](thememe.jpg)
	<br>
	memesocial.com is a web platform for sharing memes (this is a fancy way of saying a social network).
</p>


### Why does memesocial exist

Well I like memes so I said why not creating a social network just for memes.

### Getting started

Start by clonning the repo:

	mohamed@host:~/$ git clone https://github.com/mohamed-aziz/memesocial.git
	
I suggest that you create a virtual environment using virtualenv and activating it.

	mohamed@host:~/memesocial$ virtualenv venv_dev/
	mohamed@host:~/memesocial$ source venv_dev/bin/activate

Then you need to install the python packages (I use pip and you should also).

	(venv_dev)mohamed@host:~/memesocial$ pip install -r requirements.txt
	
(Don't use requirements_dev.txt that's the packages I use for python development in Emacs.)

Now you can run the development web server using:

	(venv_dev)mohamed@host:~/memesocial$ python manage.py runserver
	
Gunicorn and gevent are also installed if you want to go official and use em (someone needs to write a wrapper around gunicorn so we can run the production server using that flask script)


### Testing memesocial

I have written some tests for the API (they are broken now), you can run them using py.test

	(venv_dev)mohamed@host:~/memesocial$ py.test memesocial/tests/
	
For now we did not write coding style tests but you should go with PEP8 with the python code.

### What needs to get done

There is lots of work that needs to be done:

* We need lots and lots of work on the frontend and the design.

* We need to write some code on top of fabricjs that allows the users to create memes on the fly.


* We also need to improve my algorithms for user leaders suggestion and the news feed.

* We need some sort of trie algorithm to make a fast search feature?


### Built with

* [pallets/flask](https://github.com/pallets/flask)

* [smurfix/flask-script](https://github.com/smurfix/flask-script)

* [pallets/jinja](https://github.com/pallets/jinja)

* [coleifer/peewee](https://github.com/coleifer/peewee)

* [angular/angular.js](https://github.com/angular/angular.js)

* [jquery/jquery](https://github.com/jquery/jquery)

* [mohamed-aziz/colorpanel](https://github.com/mohamed-aziz/colorpanel)

* Emacs 24.4 with magit-mode, elpy-mode and projectile-mode.


### Authors

* **Mohamed Aziz Knani** [mohamed-aziz](https://github.com/mohamed-aziz)

* **Add your name here**

### License

This project is licensed under the GPLV3 see **LICENSE** file.

### Acknowledgments

* Thanks to [infario](https://github.com/infario) the author of [infario/colorpanel](https://github.com/infario/colorpanel).

