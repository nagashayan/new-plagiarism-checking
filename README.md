# Plagiarism-Checker

A utility to check if a document's contents are plagiarised.

## How it works

*   It searches online using Google Search API's for some queries. Queries are n-grams extracted from the source txt file.
*   Resulting URL, matched contents are checked for similarity with given text query.
*   Result of average similarity of all URL's is stored in output text file.

## Its Django 2.0 Application

* I am using Anaconda - conda environment
* use the environment.yml flie to create identical environment

 ## Steps to run the application

 * Install Anaconda
 * conda env create -f environment.yml # To create identical environment
 * source activate "environment_name"
 * python manage.py runserver #To run django server

 ## Due credits to the base repository.