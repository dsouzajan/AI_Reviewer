#!/usr/bin/env python
# coding: utf-8

# In[15]:


import os
from watson_developer_cloud import DiscoveryV1
import pandas as pd
import json
import matplotlib.pyplot as plt

def analyze_sentiment(graph):
    api_key = 'aXyV8EXAvKP3saDb3Jb6275L8MEGJdwTXxQ-CHt491B1'
    workspace_ID = 'cdf8a7x488-nlc-2954'

    discovery = DiscoveryV1(
        version="2018-01-01",
        iam_apikey=api_key,
        url="https://gateway.watsonplatform.net/discovery/api" )

    collections = discovery.list_collections('ee4527b4-f97a-4a9f-ace8-883efa3773a8').get_result()
    coll_id = collections['collections'][0]['collection_id']

    sentiment_results = []
    query_output = discovery.query(environment_id='ee4527b4-f97a-4a9f-ace8-883efa3773a8',
                                    collection_id=coll_id,
                                    #passages=True,
                                    offset=0,
                                    #count=DEFAULT_COUNT,
                                    aggregation='term(enriched_text.sentiment.document.label)',
                                    filter='',
                                    return_fields = ['text','enriched_text.sentiment.document']
                                    )
    #print(json.dumps(query_output.result['results'],indent=2))
    sentiment_results = query_output.result['results']  

    if graph:    
        df = pd.DataFrame()
        _reviews = []
        _sentiment_label = []
        _sentiment_score = []
        
        for r in sentiment_results:
            _reviews.append(r['text'])
            _sentiment_label.append(r['enriched_text']['sentiment']['document']['label'])
            _sentiment_score.append(r['enriched_text']['sentiment']['document']['score'])
        df['text'] = _reviews
        df['sentiment_label'] = _sentiment_label
        df['sentiment_score'] = _sentiment_score
        df.index = df['text']

        plt.style.use('fivethirtyeight')

        try:
            df['sentiment_label'].value_counts().plot(kind='pie', 
                                                subplots=False, 
                                                startangle=100,
                                                pctdistance=0.85,
                                                autopct='%1.1f%%',
                                                title='Sentiment of reviews')
        except:
            delete_collection = discovery.delete_collection('ee4527b4-f97a-4a9f-ace8-883efa3773a8', coll_id).get_result()
            print('collection deleted')

        plt.tight_layout()
        plt.show()
        
    delete_collection = discovery.delete_collection('ee4527b4-f97a-4a9f-ace8-883efa3773a8', coll_id).get_result()
    #print(json.dumps(delete_collection, indent=2))
    return query_output

if __name__ == '__main__':
    analyze_sentiment(graph=True)
# In[ ]:




