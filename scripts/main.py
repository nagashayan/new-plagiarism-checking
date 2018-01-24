# -*- coding: utf-8 -*-
# Master script for the plagiarism-checker
# Coded by: Shashank S Rao

#import other modules
from cosineSim import *
from htmlstrip import *
from extractdocx import *

#import required modules
import codecs
import traceback
import sys
import operator
import urllib, urllib2
import json as simplejson
# Given a text string, remove all non-alphanumeric
# characters (using Unicode definition of alphanumeric).
def getQueries(text,n):
	import re
	sentenceEnders = re.compile('[.!?]')
	sentenceList = sentenceEnders.split(text)
	sentencesplits = []
	for sentence in sentenceList:
		x = re.compile(r'\W+', re.UNICODE).split(sentence)
		x = [ele for ele in x if ele != '']
		sentencesplits.append(x)
	finalq = []
	for sentence in sentencesplits:
		l = len(sentence)
		l=l/n
		index = 0
		for i in range(0,l):
			finalq.append(sentence[index:index+n])
			index = index + n-1
		if index !=len(sentence):
			finalq.append(sentence[len(sentence)-index:len(sentence)])
	return finalq

# Search the web for the plagiarised text
# Calculate the cosineSimilarity of the given query vs matched content on google
# This is returned as 2 dictionaries 
def searchWeb(text,output,c):
	try:
		text = text.encode('utf-8')
	except:
		text =  text
	query = urllib.quote_plus(text)
	if len(query)>60:
	    return output,c
	#using googleapis for searching web
	base_url = 'https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=YOUR_APPLICATION_ID&q='
	url = base_url + '%22' + query + '%22'
	request = urllib2.Request(url,None,{'Referer':'Google Chrome'})
	response = urllib2.urlopen(request)
	results = simplejson.load(response)

	try:
		
		
	    if ( len(results) and 'searchInformation' in results and 'totalResults' in results['searchInformation'] and results['searchInformation']['totalResults'] > 0):

		    for ele in	results['items']:

			    Match = ele
			    content = Match['title']
			    if Match['link'] in output:

				    output[Match['link']] = output[Match['link']] + 1
				    c[Match['link']] = (c[Match['link']]*(output[Match['link']] - 1) + cosineSim(text,strip_tags(content)))/(output[Match['link']])
			    else:
				    output[Match['link']] = 1
				    c[Match['link']] = cosineSim(text,strip_tags(content))
	except:
		return output,c

	return output,c
    

# Use the main function to scrutinize a file for
# plagiarism
def main():
	# n-grams N VALUE SET HERE
	n=9
	if len(sys.argv) <3:
		print "Usage: python main.py <input-filename>.txt <output-filename>.txt"
		sys.exit()
	if sys.argv[1].endswith(".docx"):
	    t = docxExtract(sys.argv[1])
	else:
	    t=open(sys.argv[1],'r')
	    if not t:
		    print "Invalid Filename"
		    print "Usage: python main.py <input-filename>.txt <output-filename>.txt"
		    sys.exit()
	    t=t.read()
	queries = getQueries(t,n)
	q = [' '.join(d) for d in queries]
	found = []
	#using 2 dictionaries: c and output
	#output is used to store the url as key and number of occurences of that url in different searches as value
	#c is used to store url as key and sum of all the cosine similarities of all matches as value	
	output = {}
	c = {}
	i=1
	count = len(q)
	if count>100:
	    count=100
	for s in q[:100]:
		output,c=searchWeb(s,output,c)
		msg = "\r"+str(i)+"/"+str(count)+"completed..."
		sys.stdout.write(msg);
		sys.stdout.flush()

		i=i+1
	print "outputting to other file"
	print c
	f = open(sys.argv[2],"w")
	for ele in sorted(c.iteritems(),key=operator.itemgetter(1),reverse=True):
		print str(ele[0])+" "+str(ele[1]*100.00)
		f.write(str(ele[0])+" "+str(ele[1]*100.00))
		f.write("\n")
	f.close()
	print f
	print "\nDone!"


if __name__ == "__main__":
	try:
		main()
	except:
		#writing the error to stdout for better error detection
		error = traceback.format_exc()
		print "\nUh Oh!\n"+"Plagiarism-Checker encountered an error!:\n"+error

