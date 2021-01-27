import mysql.connector
from phpserialize import serialize, unserialize
import re
from datetime import datetime


def get_data(host, user, db, passwd, website_id):

    # connect to the database and select the wp_postmeta table
    mydb = mysql.connector.connect(host=host, user=user, database=db, passwd=passwd)
    sql_select_query = "select * from wp_postmeta where post_id={}".format(website_id)
    cursor = mydb.cursor()
    cursor.execute(sql_select_query)
    records = cursor.fetchall()
    
    main_page_url = None            # website url
    categories_links = []           # list of categories links
    next_page_selector = None      # selector for the next page in the category
    post_selector = None           # link for each post in the category
    post_title_selector = None     # title selector for the post
    product_meta = {}               # meta data dict; {old_price: str, new_price: str, product_code: str, images: list}
    
    for row in records:
        ### MAIN URL ###
        if row[2] == "_main_page_url":
            main_page_url = row[3]
        
        ### CATEGORIES ###
        if row[2] == "_category_map":
            query = bytes(row[3], encoding='utf8')
            query_unser = unserialize(query)
            for value in query_unser.values():
                categories_links.append(value.get(bytes('url', encoding='utf8')).decode('utf8'))

        ### POST SELECTORS ###
        if row[2] == "_category_post_link_selectors":
            query = bytes(row[3], encoding='utf8')
            query_unser = unserialize(query)
            post_selector = query_unser.get(0).get(bytes('selector', encoding='utf8')).decode('utf8')
            # for value in query_unser.values():
            #     post_selectors.append(value.get(bytes('selector', encoding='utf8')).decode('utf8')) 

        ### CATEGORY NEXT PAGE SELECTORS ###
        if row[2] == '_category_next_page_selectors':
            query = bytes(row[3], encoding='utf8')
            query_unser = unserialize(query)
            next_page_selector = query_unser.get(0).get(bytes('selector', encoding='utf8')).decode('utf8')
            # for value in query_unser.values():
            #     next_page_selectors.append(value.get(bytes('selector', encoding='utf8')).decode('utf8'))
        
        ### POST Title Selectors ###
        if row[2] == "_post_title_selectors":
            query = bytes(row[3], encoding='utf8')
            query_unser = unserialize(query)
            post_title_selector = query_unser.get(0).get(bytes('selector', encoding='utf8')).decode('utf-8')
            # for value in title_sel_unser.values():
            #     post_title_selectors.append(value.get(bytes('selector', encoding='utf8')).decode('utf-8'))

        ### PRODUCT META DATA (OLD PRICE, NEW PRICE,...)
        if row[2] == '_post_custom_meta_selectors':
            query = bytes(row[3], encoding = 'utf8')
            query_unser = unserialize(query)
            for value in query_unser.values():
                product_meta[value.get(bytes('meta_key', encoding='utf8')).decode('utf8')] = value.get(bytes('selector', encoding='utf8')).decode('utf8')
                # print(value.get(bytes('meta_key', encoding='utf8')).decode('utf8'))
                # print(value.get(bytes('selector', encoding='utf8')).decode('utf8'))
            
    return main_page_url, categories_links, post_selector, next_page_selector, post_title_selector, product_meta


# main_page_url, categories_links, post_selector, next_page_selector, post_title_selector, product_meta = get_data(host="localhost", user="root", db="plugin_test", passwd="", website_id=246)
# print(product_meta)

import time
seconds = time.time()
print("Seconds since epoch =", seconds)