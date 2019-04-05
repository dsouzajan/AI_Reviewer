#!/usr/bin/env python
# coding: utf-8

# In[13]:


#!/usr/bin/env python
# coding: utf-8

# In[50]:


from lxml import html
from json import dump, loads
from requests import get
import json
from re import sub
from dateutil import parser as dateparser
from time import sleep
from io import BytesIO
import fpdf
import os
from watson_developer_cloud import DiscoveryV1
import pandas as pd
import json
import matplotlib.pyplot as plt

api_key = 'aXyV8EXAvKP3saDb3Jb6275L8MEGJdwTXxQ-CHt491B1'
workspace_ID = 'cdf8a7x488-nlc-2954'

discovery = DiscoveryV1(
    version="2018-01-01",
    iam_apikey=api_key,
    url="https://gateway.watsonplatform.net/discovery/api" )

def ParseReviews(asin,idd):
    # This script has only been tested with Amazon.com
    amazon_url = 'http://www.amazon.com/dp/' + asin
    # Add some recent user agent to prevent amazon from blocking the request
    # Find some chrome user agent strings  here https://udger.com/resources/ua-list/browser-detail?browser=Chrome
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    for i in range(5):
        response = get(amazon_url, headers=headers, verify=False, timeout=30)
        if response.status_code == 404:
            return {"url": amazon_url, "error": "page not found"}
        if response.status_code != 200:
            continue

        # Removing the null bytes from the response.
        cleaned_response = response.text.replace('\x00', '')

        parser = html.fromstring(cleaned_response)
        XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
        XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
        XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'
        XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
        XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
        XPATH_PRODUCT_PRICE = '//span[@id="priceblock_ourprice"]/text()'

        raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
        raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
        total_ratings = parser.xpath(XPATH_AGGREGATE_RATING)
        reviews = parser.xpath(XPATH_REVIEW_SECTION_1)

        product_price = ''.join(raw_product_price).replace(',', '')
        product_name = ''.join(raw_product_name).strip()

        if not reviews:
            reviews = parser.xpath(XPATH_REVIEW_SECTION_2)
        ratings_dict = {}
        reviews_list = []

        # Grabing the rating  section in product page
        for ratings in total_ratings:
            extracted_rating = ratings.xpath('./td//a//text()')
            if extracted_rating:
                rating_key = extracted_rating[0]
                raw_raing_value = extracted_rating[1]
                rating_value = raw_raing_value
                if rating_key:
                    ratings_dict.update({rating_key: rating_value})

        # Parsing individual reviews
        for review in reviews:
            XPATH_RATING = './/i[@data-hook="review-star-rating"]//text()'
            XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
            XPATH_REVIEW_POSTED_DATE = './/span[@data-hook="review-date"]//text()'
            XPATH_REVIEW_TEXT_1 = './/div[@data-hook="review-collapsed"]//text()'
            XPATH_REVIEW_TEXT_2 = './/div//span[@data-action="columnbalancing-showfullreview"]/@data-columnbalancing-showfullreview'
            XPATH_REVIEW_COMMENTS = './/span[@data-hook="review-comment"]//text()'
            XPATH_AUTHOR = './/span[contains(@class,"profile-name")]//text()'
            XPATH_REVIEW_TEXT_3 = './/div[contains(@id,"dpReviews")]/div/text()'

            raw_review_author = review.xpath(XPATH_AUTHOR)
            raw_review_rating = review.xpath(XPATH_RATING)
            raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
            raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
            raw_review_text1 = review.xpath(XPATH_REVIEW_TEXT_1)
            raw_review_text2 = review.xpath(XPATH_REVIEW_TEXT_2)
            raw_review_text3 = review.xpath(XPATH_REVIEW_TEXT_3)

            # Cleaning data
            author = ' '.join(' '.join(raw_review_author).split())
            review_rating = ''.join(raw_review_rating).replace('out of 5 stars', '')
            review_header = ' '.join(' '.join(raw_review_header).split())

            try:
                review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
            except:
                review_posted_date = None
            review_text = ' '.join(' '.join(raw_review_text1).split())

            # Grabbing hidden comments if present
            if raw_review_text2:
                json_loaded_review_data = loads(raw_review_text2[0])
                json_loaded_review_data_text = json_loaded_review_data['rest']
                cleaned_json_loaded_review_data_text = re.sub('<.*?>', '', json_loaded_review_data_text)
                full_review_text = review_text + cleaned_json_loaded_review_data_text
            else:
                full_review_text = review_text
            if not raw_review_text1:
                full_review_text = ' '.join(' '.join(raw_review_text3).split())

            raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)
            review_comments = ''.join(raw_review_comments)
            review_comments = sub('[A-Za-z]', '', review_comments).strip()
            review_dict = {
                'review_comment_count': review_comments,
                'review_text': full_review_text,
                'review_posted_date': review_posted_date,
                'review_header': review_header,
                'review_rating': review_rating,
                'review_author': author

            }
            extracted_data = []
            extracted_data.append(review_dict['review_text'])

            #f = open(review_dict['review_author']+'.json', 'w')
            #dump(extracted_data, f, indent=4)
            #f.close()
            author = review_dict['review_author']
            json_string = json.dumps(extracted_data)
            pdf = fpdf.FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.write(5,txt=json_string)
            pdf.output(r"C:\Users\Janice Dsouza\Desktop\AI and analytics\Project Test\Reviews\1" + author + '.pdf','F')
            with open(r"C:\Users\Janice Dsouza\Desktop\AI and analytics\Project Test\Reviews\1" + author + '.pdf','rb') as fileinfo:
                add_doc = discovery.add_document('ee4527b4-f97a-4a9f-ace8-883efa3773a8', idd, file=fileinfo, file_content_type='application/pdf').get_result()
            #print(json.dumps(add_doc, indent=2))
            reviews_list.append(review_dict)

        data = {
            'ratings': ratings_dict,
            'reviews': reviews_list,
            'url': amazon_url,
            'name': product_name,
            'price': product_price

        }
        return data

    return {"error": "failed to process the page", "url": amazon_url}

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def ReadAsin(url,i):
    a=find_nth(url,"/",5)
    #print(a)

    asin=url[a+1:a+11]

    extracted_data = ""
    print("Downloading and processing page http://www.amazon.com/dp/" + asin)
    extracted_data = (ParseReviews(asin,i))
    #print (extracted_data)
    #return extracted_data
    
def discovery_create():
    configs = discovery.list_configurations('ee4527b4-f97a-4a9f-ace8-883efa3773a8').get_result()
    #print(json.dumps(configs, indent=2))
    config_id = configs['configurations'][0]['configuration_id']
    
    new_collection = discovery.create_collection(environment_id='ee4527b4-f97a-4a9f-ace8-883efa3773a8', 
                                                 configuration_id=config_id, name='My Collection', 
                                                 description='Reviews', language='en').get_result()
    collection_id = new_collection['collection_id']
    #print(collection_id)
    return collection_id


# In[ ]:





if __name__ == '__main__':
    ID = discovery_create()
    url = input("Enter URL: ")
    ReadAsin(url,ID)


# In[51]:



# In[ ]:




