
# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from flask import Flask, jsonify, request,render_template
from urllib import request as req
from watson_developer_cloud import NaturalLanguageClassifierV1
from Reviews_discovery import discovery_create, ReadAsin
from Sentiment_discovery import analyze_sentiment

#We are setting the rootpath for our website
app = Flask(__name__)


workspace_ID = 'bef893x499-nlc-404' #Your Workspace ID goes here
api_Key = 'CiGTgOcVkzhRL8ofWWESIEp2waMORQk_gUnF1UrwEPxl' #Your iam_apikey goes here

#Create a NaturalLanguageClassiferV1 object
natural_language_classifier = NaturalLanguageClassifierV1(
    iam_apikey= api_Key)


#This connects this Python File to the root directory of our website
#If we wanted to connect to a different website we would say
#@app.route('/about_Page')
#This function is now mapped to our webpage
#This has to return something to the webpage
@app.route('/')
def Welcome():
    return render_template('test.html')
  
@app.route('/analyze', methods=['GET', 'POST'])
def Analyze():    #Gets the inputted string from the user
    url = request.form['text']

    print(url)
    ID = discovery_create()
    #Empty String is passed if text isn't entered
    #reviews = ""
    ReadAsin(url, ID)
    output = analyze_sentiment(graph=False)

    #If text box isn't empty, do the following
    #if comment_text != "":
        #Creates an instance of our natural language classifer with the provided next
        #classes = natural_language_classifier.classify(workspace_ID, comment_text)
        #Parses the 'DetailedResponse' object provided by the API call
   # results = "hello"
    results=[]
    for i in range(len(output.result["results"])):

        results.append(output.result["results"][i]['enriched_text']['sentiment']['document']['score'])
        #for item in results
    print (output)
    print(results)
    #Displays it the window
    msg=[0.65,0.65,0.43,343]
    #msg="shoe this"
    return jsonify(msg)
    
# Define the Random Comment Route
# This route simply selects a comment at random from the 
#   complete CSV of all of the Amazon reviews
