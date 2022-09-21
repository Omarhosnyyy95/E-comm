import scrapy
import scrapy
import mysql.connector
from phpserialize import serialize, unserialize
import re
from datetime import datetime

class MortoglouSpider(scrapy.Spider):
    name = 'mortoglou'
    allowed_domains = ['www.mortoglou.gr']

    def get_data(self, host, user, db, passwd, website_id):

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
    
    # access the website
    def start_requests(self):
        
        # main_page_url, categories_links, post_selector, next_page_selector, post_title_selector, product_meta = self.get_data(host="localhost", user="root", db="plugin_test", passwd="", website_id=252)
        main_page_url = 'https://www.mortoglou.gr/'
        categories = {
            'Women': 'https://www.mortoglou.gr/gunaikeia-el', 
            'Men': 'https://www.mortoglou.gr/andrika-el', 
            'Children': 'https://www.mortoglou.gr/paidika-el', 
            'Timberland Corner': 'https://www.mortoglou.gr/timberland-el', 
            'Accessory': 'https://www.mortoglou.gr/all-products-el?ff2=4', 
            }

        products_sel = "//div[@class='main-products product-grid']/div"
        product_link_sel = ".//div[@class='image']/a/@href"
        product_image_sel = ".//div[@class='image']/a//img[1]/@src"
        product_title_sel = ".//div[@class='name']/a/text()"
        product_brand_sel = ".//div[@class='stats']/span/span/a/text()"
        product_code_sel = ".//div[@class='name']/a/text()"
        old_price_sel = ".//div[@class='price']/div/span[@class='price-old']/text()"
        new_price_sel = ".//div[@class='price']/div/span[@class='price-new']/text()"
        price_sel = ".//div[@class='price']/div/span[@class='price-normal']/text()"
        next_page_sel = "//ul[@class='pagination']/li/a[@class='next']/@href"   # absolute url

        for category_name, category_url in categories.items():
            yield scrapy.Request(
                # url=category_link,
                url=category_url,
                callback=self.parse,
                meta={
                    "main_page_url": main_page_url,
                    "category_name": category_name,
                    "products_sel": products_sel,
                    "product_link_sel": product_link_sel,
                    "product_image_sel": product_image_sel,
                    "product_title_sel": product_title_sel,
                    "product_brand_sel": product_brand_sel,
                    "product_code_sel": product_code_sel,
                    "old_price_sel": old_price_sel,
                    "new_price_sel": new_price_sel,
                    "price_sel": price_sel,
                    "next_page_sel": next_page_sel
                },
                # dont_filter=False
            )


    def parse(self, response):
        scraping_time = datetime.now()
        main_page_url = response.meta['main_page_url']
        category_name = response.meta['category_name']
        products_sel = response.meta['products_sel']
        product_link_sel = response.meta['product_link_sel']
        product_image_sel = response.meta['product_image_sel']
        product_title_sel = response.meta['product_title_sel']
        product_brand_sel = response.meta['product_brand_sel']
        product_code_sel = response.meta['product_code_sel']
        old_price_sel = response.meta['old_price_sel']
        new_price_sel = response.meta['new_price_sel']
        price_sel = response.meta['price_sel']
        next_page_sel = response.meta['next_page_sel']

        products = response.xpath(products_sel)
        for product in products:
            product_link = product.xpath(product_link_sel).get()
            product_image = product.xpath(product_image_sel).get()
            product_title = product.xpath(product_title_sel).get()
            product_brand = product.xpath(product_brand_sel).get()
            product_code = product.xpath(product_code_sel).get()
            old_price = product.xpath(old_price_sel).get()
            new_price = product.xpath(new_price_sel).get()
            price = product.xpath(price_sel).get()

            yield{
                'scraping_time': scraping_time,
                'website_id': 23,
                'main_website_url': main_page_url,
                'category_name': category_name,
                'product_link': product_link,
                'product_title': product_title,
                'old_price': old_price,
                'new_price': new_price,
                'price': price,
                'brand': product_brand,
                'product_code': product_code,
                'images': product_image,
            }
            
            
        next_page = response.xpath(next_page_sel).get()
        if next_page:
            yield scrapy.Request(
                url = next_page,
                callback=self.parse,
                meta={
                    "main_page_url": main_page_url,
                    "category_name": category_name,
                    "products_sel": products_sel,
                    "product_link_sel": product_link_sel,
                    "product_image_sel": product_image_sel,
                    "product_title_sel": product_title_sel,
                    "product_brand_sel": product_brand_sel,
                    "product_code_sel": product_code_sel,
                    "old_price_sel": old_price_sel,
                    "new_price_sel": new_price_sel,
                    "price_sel": price_sel,
                    "next_page_sel": next_page_sel
                },
            )
    # # access the categories page
    # def category_page(self, response):
    #     main_page_url = response.meta['main_page_url']
    #     category_name = response.meta['category_name']
    #     post_selector = response.meta['post_selector']
    #     next_page_selector = response.meta['next_page_selector']
    #     post_title_selector = response.meta['post_title_selector']
    #     product_meta = response.meta['product_meta']
    #     products = [link for link in response.css(post_selector+"::attr(href)").getall()]
    #     # product = "https://www.myshoe.gr" + response.css(post_selector+"::attr(href)").get()
    #     for product in products:
    #         yield scrapy.Request(
    #             url=product,
    #             callback=self.parse,
                
    #             meta={
    #                 "main_page_url": main_page_url,
    #                 "category_name": category_name,
    #                 "post_title_selector": post_title_selector,
    #                 "product_meta": product_meta
    #             }
    #         )
    #     next_page = response.css(next_page_selector+"::attr(href)").get()
    #     if next_page:
    #         yield scrapy.Request(
    #             url = next_page,
    #             callback=self.category_page,
    #             meta={
    #                 "main_page_url": main_page_url,
    #                 "category_name": category_name,
    #                 "post_selector": post_selector,
    #                 "next_page_selector": next_page_selector,
    #                 "post_title_selector": post_title_selector,
    #                 "product_meta": product_meta
    #             }
    #         )
    
    # def parse(self, response):
    #     scraping_time = datetime.now()
    #     main_page_url = response.meta['main_page_url']
    #     category_name = response.meta['category_name']
    #     post_title_selector = response.meta['post_title_selector']
    #     product_meta = response.meta['product_meta']
    #     post_link = response.url
        

        
    #     old_price_sel = product_meta.get('old_price')
    #     new_price_sel = product_meta.get('new_price')
    #     price_sel = product_meta.get('price')
    #     product_code_sel = product_meta.get('product_code')
    #     brand_sel = product_meta.get('brand')
    #     images_sel = product_meta.get('images')
        
       

    #     title = response.css(post_title_selector+"::text").get()
    #     old_price = response.css(old_price_sel+"::text").get()
    #     new_price = response.css(new_price_sel+"::text").get()
    #     price = response.css(price_sel+"::text").get()
    #     product_code = response.css(product_code_sel+"::text").get()
    #     brand = response.css(brand_sel+"::text").get()
    #     # images = response.css(images_sel).attrib['src']
    #     images = [res.attrib['src'] for res in response.css(images_sel)]
        
        
        
    #     yield{
    #         "scraping_time": scraping_time,
    #         "website_id": 252,
    #         "main_website_url": main_page_url,
    #         "category_name": category_name,
    #         'product_link': post_link,
    #         "product_title": title,
    #         'old_price': old_price,
    #         'new_price': new_price,
    #         'price': price,
    #         'brand': brand,
    #         'product_code': product_code,
    #         'images': images[0],
    #     }
