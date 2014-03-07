TasksLoad
=========

Python for Android SL4A script to load last Google Tasks using Google Tasks API into Zooper Widget variable


Summary
=======
This Py4A script does load tasks list from Google Tasks using Google tasks API and then sets Zooper Widget variable with next format: 

dd.mm hh:mm: task1 caption

dd.mm hh:mm: task2 caption

Installation
============
You need to put tasks_load.py into /sdcard/sl4a/scripts next to client_secrets.json downloaded from your Google API application
Next set up running this script at some interval or action trigger.
In Zooper Widget you need to add Rich text module with text #TNextTask#.
