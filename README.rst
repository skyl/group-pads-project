Pinax-group-pads
================

Simple ``realtime`` collaborative editing with orbited and twisted integrated into a basic
pinax project with a basic group.  Boilerplate for django-orbited-twisted + pinax.


TODO-

  * default templates
  * group awareness


Install
=======

Grab a copy of dev pinax looking toward 0.9.  
Install the requirements and get into the env.

Add twisted and orbited to the env::

    pip install -U twisted; pip install orbited

Syncdb and run the server::

    twistd -ny serverpad.py

Now you can go to http://127.0.0.1:8000/pads/new/ to create a pad.
Login with another user to the pad with another browser and enjoy the Comet action :D


