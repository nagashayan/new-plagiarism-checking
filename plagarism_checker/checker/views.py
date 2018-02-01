# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from cosineSim import *
from htmlstrip import *
import json

#import required modules
import codecs
import traceback
import sys
import operator
import urllib, urllib2
import json as simplejson
import requests
import pdb;
# Given a text string, remove all non-alphanumeric
# characters (using Unicode definition of alphanumeric).
def getQueries(text, n):
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
        l = l / n
        index = 0
        for i in range(0, l):
            finalq.append(sentence[index:index + n])
            index = index + n - 1
        if index != len(sentence):
            finalq.append(sentence[len(sentence) - index:len(sentence)])
    return finalq


# Search the web for the plagiarised text
# Calculate the cosineSimilarity of the given query vs matched content on google
# This is returned as 2 dictionaries
def searchWeb(text, output, c):
    try:
        text = text.encode('utf-8')
    except:
        text = text
    query = urllib.quote_plus(text)
    if len(query) > 60:
        return output, c
    # using googleapis for searching web
    payload = {'q' :  query, 'cx': 'YOUR_APP_ID', 'key': 'YOUR_API_KEY'}
    base_url = 'https://www.googleapis.com/customsearch/v1'

    custom_headers = {'Referer':'Google Chrome'}
    response = requests.get(base_url,params=payload,headers=custom_headers)

    results = response.json()

    # print results
    try:

        if (len(results) and 'searchInformation' in results and 'totalResults' in results['searchInformation'] and
                    results['searchInformation']['totalResults'] > 0):

            for ele in results['items']:

                Match = ele
                content = Match['title']
                if Match['link'] in output:
                    # print text
                    # print strip_tags(content)
                    output[Match['link']] = output[Match['link']] + 1
                    c[Match['link']] = (c[Match['link']] * (output[Match['link']] - 1) + cosineSim(text, strip_tags(
                        content))) / (output[Match['link']])
                else:
                    output[Match['link']] = 1
                    c[Match['link']] = cosineSim(text, strip_tags(content))
    except:
        return output, c

    return output, c

#Main View
@csrf_exempt
def processInput(request):
    try:
        final_results = {}
        no_match = True
        init = True
        if 'check-text' in request.POST:

            t = request.POST['check-text']

            # n-grams N VALUE SET HERE
            n = 9

            queries = getQueries(t, n)
            q = [' '.join(d) for d in queries]
            found = []
            # using 2 dictionaries: c and output
            # output is used to store the url as key and number of occurences of that url in different searches as value
            # c is used to store url as key and sum of all the cosine similarities of all matches as value
            output = {}
            c = {}
            i = 1
            count = len(q)
            if count > 100:
                count = 100

            for s in q[:100]:
                if s == '':
                    continue

                output, c = searchWeb(s, output, c)
                msg = "\r" + str(i) + "/" + str(count) + "completed..."

                i = i + 1
            # print "\n"

        # final_results = {'https://solutions.softonic.com/movies/death-note-desu-noto': str(0.5477225575051661),
        #                   'http://www.regione.lombardia.it/wps/wcm/connect/b99d117e-4508-4d54-9308-6c568cc20b7e/DOCUMENTAZIONE++da+allegare++alle+istanze+di+autorizzazione+paesaggistica+semplificata.doc?MOD=AJPERES&CACHEID=b99d117e-4508-4d54-9308-6c568cc20b7e': str(0.5477225575051661),
        #                   'http://www.playbill.com/article/frank-wildhorn-musical-death-note-has-nyc-reading-with-andy-kelso-robert-cuccioli-and-adrienne-warren-prior-to-japanese-premiere-com-217333': str(0.5477225575051661),
        #                   'https://www.youtube.com/watch?v=ziLu9FCaBFk': str(0.5477225575051661),
        #                   'http://www.firstpost.com/entertainment/death-note-before-netflixs-film-a-look-at-the-original-dexter-meets-sherlock-anime-series-3954027.html': str(0.5477225575051661)}

            for ele in sorted(c.iteritems(), key=operator.itemgetter(1), reverse=True):
                percent = math.ceil(ele[1] * 100.00)
                if percent > 5:
                    final_results[str(ele[0])] = str(percent) + "%"

            print "\nDone!"

            if len(final_results) > 0:
                no_match = False
            init = False

        return render(request, "index.html", {'results': final_results, 'no_match': no_match, 'init': init})

    except Exception as e:
        print 'Error ' + str(e)

def mysite_contact(request):
    
    requests.post(
        "https://api.mailgun.net/v3/sandbox7abe41e40f174ef18cf6ff5884e81427.mailgun.org/messages",
        auth=("api", "key-5ee449c0c134246c6dffaeb48d88adb6"),
        data={"from": "Mailgun Sandbox <postmaster@sandbox7abe41e40f174ef18cf6ff5884e81427.mailgun.org>",
              "to": "NAGASHAYANA RAMAMURTHY <nagashayan1@gmail.com>",
              "subject": "Hello NAGASHAYANA RAMAMURTHY",
              "text": "Congratulations NAGASHAYANA RAMAMURTHY, you just sent an email with Mailgun!  You are truly awesome!"})

    return HttpResponse(json.dumps({"success": "True"}), status=200)
#default error handlers

def handler404(request):

    return render(request, "404.html", {}, status=404)


def handler500(request):
    return render(request, "500.html", {}, status=500)