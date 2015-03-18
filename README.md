# recipe-transform


### To run server to perform transforms, make sure to install required python packages.
Either install globally or in virtualenv using the following command:

	pip install -r requirements.txt

Note: we use NLTK for processing, and in the case that you don't have the NLTK corpus downloaded, run the following:
	
	python 
Once inside python, run the following two commands:
	
	import nltk
	nltk.download()
	
NLTK will produce a GUI that you can use to install said packages.

Once packages are there, to run the transformation server, run the following:

	python manage.py runserver

Visit 127.0.0.1:5000/index to begin the process.

### Autograder Instructions

To run the autograder, navigate to the Scraper folder.  Once there, you may run the following:
	
	python autograder.py url
	
This will load all of the recipes in the Recipes folder and compare our own results to theirs.

