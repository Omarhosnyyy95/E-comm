import scrapy
import re
import mysql.connector
from phpserialize import serialize, unserialize
from datetime import datetime
from scrapy_splash import SplashRequest

class WomenSpider(scrapy.Spider):
    name = 'myshoe'
    allowed_domains = ['www.myshoe.gr']
    # start_urls = ['https://www.koolfly.com/en/woman']

    # access the database
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
        
        # main_page_url, categories_links, post_selector, next_page_selector, post_title_selector, product_meta = self.get_data(host="localhost", user="root", db="plugin_test", passwd="", website_id=246)
        
        main_page_url = 'https://www.myshoe.gr/'
        # categories_links = ['https://www.tsakirismallas.gr/en/category/126784/women/', 'https://www.tsakirismallas.gr/en/category/126724/men/', 'https://www.tsakirismallas.gr/en/category/126722/kids/', 'https://www.tsakirismallas.gr/en/category/126715/bags/', 'https://www.tsakirismallas.gr/en/category/126719/accessories/']
        categories = {
            'Women': 'https://www.myshoe.gr/gynaikeia/gynaikeia-papoytsia_s-66762.aspx', 
            'Men': 'https://www.myshoe.gr/andrika/andrika-papoytsia_s-66911.aspx', 
            'Children': 'https://www.myshoe.gr/paidika/paidikh-syllogh-papoytsiwn_s-66912.aspx', 
            'Bags': 'https://www.tsakirismallas.gr/en/category/126715/bags/', 
            'Accessory': 'https://www.myshoe.gr/aksesoyar/accessories_s-67031.aspx', 
            }

        products_sel = "//ul[@class='divRow']/li"
        product_link_sel = ".//a/@href" # absolute link
        product_image_sel = ".//a/div/div[@class='ProductImage']/img/@src"
        product_title_sel = ".//a/div/div[@class='ProductImage']/img/@title"
        product_brand_sel = ".//a/div/div[@class='product-list-details']/div[@class='brand']/text()"
        product_code_sel = ".//a/div/div[@class='ProductImage']/img/@title"
        old_price_sel = ".//a/div/div[@class='product-list-details']/div[@class='price']/div[@class='old-price']/text()"
        new_price_sel = ".//a/div/div[@class='product-list-details']/div[@class='price']/text()"
        price_sel = "a/div/div[@class='product-list-details']/div[@class='price']/text()"
        next_page_sel = "(//div[@class='filters']/div/a)[last()]/@href" # absolute link
        
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
        

    #     old_price_sel = product_meta.get('old_price')
    #     new_price_sel = product_meta.get('new_price')
    #     price_sel = product_meta.get('price')
        
        
    #     # images = product_meta.get('images')


    #     old_price = response.css(old_price_sel+"::text").get()
    #     new_price = response.css(new_price_sel+"::text").get()
    #     price = response.css(price_sel+"::text").get()
        
    #     # images = response.css(images_sel).attrib['data-src']
    #     # images = response.css(images_sel)

        
        
    #     products = ["https://www.myshoe.gr" + link for link in response.css(post_selector+"::attr(href)").getall()]
        
    #     # "https://www.myshoe.gr" + response.css(post_selector+"::attr(href)").getall()
    #     # product = "https://www.myshoe.gr" + response.css(post_selector+"::attr(href)").get()
        
    #     for product in products:
    #         yield scrapy.Request(
    #             url=product,
    #             callback=self.parse,
    #             # args={
    #             #     'wait': 0.5,
    #             # },
    #             meta={
    #                 "main_page_url": main_page_url,
    #                 "category_name": category_name,
    #                 "post_title_selector": post_title_selector,
    #                 "product_meta": product_meta,
    #                 "old_price": old_price,
    #                 "new_price": new_price,
    #                 "price": price,
    #                 # "brand": brand,
    #                 # "images": images,
                    
    #             }
    #         )

    #     # for product in products:
    #     #     yield SplashRequest(
    #     #         url=product,
    #     #         callback=self.parse,
    #     #         args={
    #     #             'wait': 0.5,
    #     #         },
    #     #         meta={
    #     #             "main_page_url": main_page_url,
    #     #             "post_title_selector": post_title_selector,
    #     #             "product_meta": product_meta
    #     #         }
    #     #     )

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
    
    # # parse the required items
    # def parse(self, response):
    #     scraping_time = datetime.now()
    #     main_page_url = response.meta['main_page_url']
    #     category_name = response.meta['category_name']
    #     post_title_selector = response.meta['post_title_selector']
    #     product_meta = response.meta['product_meta']
    #     post_link = response.url
    #     old_price = response.meta['old_price']
    #     new_price = response.meta['new_price']
    #     price = response.meta['price']
    #     # images = response.meta['images']
    #     # brand = response.meta['brand']

        
    #     # old_price_sel = product_meta.get('old_price')
    #     # new_price_sel = product_meta.get('new_price')
    #     # price_sel = product_meta.get('price')
    #     product_code_sel = product_meta.get('product_code')
    #     brand_sel = product_meta.get('brand')
    #     images_sel = product_meta.get('images')
        
       

    #     title = response.css(post_title_selector+"::text").get()
    #     # old_price = response.css(old_price_sel+"::text").get()
    #     # new_price = response.css(new_price_sel+"::text").get()
    #     # price = response.css(price_sel+"::text").get()
    #     product_code = response.css(product_code_sel+"::text").getall()[0].split()[-1]
    #     brand = response.css(brand_sel+"::text").get()
    #     images =  response.css(images_sel).attrib['src']
    #     # images = [res.attrib['src'] for res in response.css(images_sel)]
        
        
        
    #     yield{
    #         "scraping_time": scraping_time,
    #         "website_id": 246,
    #         "main_website_url": main_page_url,
    #         "category_name": category_name,
    #         'product_link': post_link,
    #         "product_title": title,
    #         'old_price': old_price,
    #         'new_price': new_price,
    #         'price': price,
    #         'brand': brand,
    #         'product_code': product_code,
    #         'images': images,
    #     }
    #     # for key, value in post_meta.items():
    #     #     selector = value[0]
    #     #     meta_value = response.css(selector+"::text").get()
        

    #     # title = response.css(title_selector+"::text").get()
        
        
    #     # products = response.xpath("//li[@class='col-md-4 col-sm-6 col-xs-12 item']")
    #     # for product in products:
    #     #     link = product.xpath(".//a/@href").get()
    #     #     title = product.xpath(".//a/@title").get()
    #     #     category = product.xpath(".//a/@data-category").get()
    #     #     image = product.xpath(".//a[1]/span[1]/img/@src").get()
    #     #     brand = product.xpath(".//h4/text()").get()
    #     #     name = product.xpath(".//h3/a[2]/text()").get()
    #     #     old_price = product.xpath(".//p[@class='old-price']/span[2]/text()").get()
    #     #     current_price = product.xpath(".//p[@class='special-price']/span[2]/text()").get()

    #     #     yield{
    #     #         "product_name": name,
    #     #         "product_brand": brand,
    #     #         "product_link": link,
    #     #         "product_image": image,
    #     #         "product_category": category,
    #     #         "old_price": old_price,
    #     #         "special_price": current_price,
    #     #     }

    #     # next_page = response.xpath("(//a[@class='next i-next'])[2]/@href").get()
    #     # if next_page:
    #     #     yield scrapy.Request(url = next_page, callback=self.parse)
        
        

