import scrapy
from datetime import datetime


class TsakirismallasSpider(scrapy.Spider):
    name = 'tsakirismallas'
    allowed_domains = ['www.tsakirismallas.gr']
    # start_urls = ['http://www.tsakirismallas.gr/en/']
    # access the website
    
    def start_requests(self):
        
        # main_page_url, categories_links, post_selector, next_page_selector, post_title_selector, product_meta = self.get_data(host="localhost", user="root", db="plugin_test", passwd="", website_id=246)
        
        ## add https to the domain url ** important
        main_page_url = 'www.tsakirismallas.gr/en'
        # categories_links = ['https://www.tsakirismallas.gr/en/category/126784/women/', 'https://www.tsakirismallas.gr/en/category/126724/men/', 'https://www.tsakirismallas.gr/en/category/126722/kids/', 'https://www.tsakirismallas.gr/en/category/126715/bags/', 'https://www.tsakirismallas.gr/en/category/126719/accessories/']
        categories = {
            'Women': 'https://www.tsakirismallas.gr/en/category/126784/women/', 
            'Men': 'https://www.tsakirismallas.gr/en/category/126724/men/', 
            'Kids': 'https://www.tsakirismallas.gr/en/category/126722/kids/', 
            'Bags': 'https://www.tsakirismallas.gr/en/category/126715/bags/', 
            'Accessory': 'https://www.tsakirismallas.gr/en/category/126719/accessories/', 
            }
        
        products_sel = "//div[@id='masonryContainer']/div[@class='productBlock']"
        product_link_sel = ".//div[@class='productImage']/a/@href"  # absolute link
        product_image_sel = ".//div[@class='productImage']/a/img/@data-src"
        product_title_sel = ".//div[@class='productInfo']/div[1]/text()"
        product_brand_sel = ".//div[@class='productInfo']/div[1]/text()"
        product_code_sel = ".//div[@class='productImage']/a/@data-product-id"
        old_price_sel = ".//div[@class='productInfo']/div[@class='price']/span[@class='oldPrice']/text()"
        new_price_sel = ".//div[@class='productInfo']/div[@class='price']/span[2]/text()"
        price_sel = ".//div[@class='productInfo']/div[@class='price']/text()"
        next_page_sel = "//a[@class='next']/@href"  # absolute link

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




        # post_selector = 'div.productImage a'
        # next_page_selector = 'a.next'
        # post_title_selector = '#Tab1Content #ShownDesc'
        # product_meta = {'images': 'div.productImage a img', 'old_price': 'div.product div.price span.oldPrice', 'new_price':'div.product div.price', 'price':'div.product div.price', 'brand':'div.product div.brand', 'product_code': 'div.product-style'}

        # for category_name, category_url in categories.items():
        #     yield scrapy.Request(
        #         url=category_url,
        #         callback=self.category_page,
        #         meta={
        #             "main_page_url": main_page_url,
        #             "category_name": category_name,
        #             "post_selector": post_selector,
        #             "next_page_selector": next_page_selector,
        #             "post_title_selector": post_title_selector,
        #             "product_meta": product_meta
        #         }        
        #     )
  
        # for category_link in categories_links:
        #     yield scrapy.Request(
        #         url=category_link,
        #         callback=self.category_page,
        #         meta={
        #             "main_page_url": main_page_url,
        #             "post_selector": post_selector,
        #             "next_page_selector": next_page_selector,
        #             "post_title_selector": post_title_selector,
        #             "product_meta": product_meta
        #         }        
                
        #     )
        # for category_link in categories_links:
        # yield scrapy.Request(
        #     # url=category_link,
        #     url=categories_links[0],
        #     callback=self.category_page,
        #     meta={
        #         "main_page_url": main_page_url,
        #         "post_selector": post_selector,
        #         "next_page_selector": next_page_selector,
        #         "post_title_selector": post_title_selector,
        #         "product_meta": product_meta
        #     }
        # )
    
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
    #     brand_sel = product_meta.get('brand')
    #     images_sel = product_meta.get('images')
    #     # images = product_meta.get('images')


    #     old_price = response.css(old_price_sel+"::text").get()
    #     new_price = response.css(new_price_sel+"::text").get()
    #     price = response.css(price_sel+"::text").get()
    #     brand = response.css(brand_sel+"::text").get()
    #     images = response.css(images_sel).attrib['data-src']
    #     # images = response.css(images_sel)

    #     products = [link for link in response.css(post_selector+"::attr(href)").getall()]
        
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
    #                 "brand": brand,
    #                 "images": images,
                    
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
    #     images = response.meta['images']
    #     brand = response.meta['brand']

        
    #     # old_price_sel = product_meta.get('old_price')
    #     # new_price_sel = product_meta.get('new_price')
    #     # price_sel = product_meta.get('price')
    #     product_code_sel = product_meta.get('product_code')
    #     # brand_sel = product_meta.get('brand')
    #     # images_sel = product_meta.get('images')
        
       

    #     title = response.css(post_title_selector+"::text").get()
    #     # old_price = response.css(old_price_sel+"::text").get()
    #     # new_price = response.css(new_price_sel+"::text").get()
    #     # price = response.css(price_sel+"::text").get()
    #     product_code = response.css(product_code_sel+"::text").getall()[1]
    #     # images = response.css(images_sel.attrib['src'])
    #     # brand = response.css(brand_sel+"::text").get()

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

        # for key, value in post_meta.items():
        #     selector = value[0]
        #     meta_value = response.css(selector+"::text").get()
        

        # title = response.css(title_selector+"::text").get()
        
        
        # products = response.xpath("//li[@class='col-md-4 col-sm-6 col-xs-12 item']")
        # for product in products:
        #     link = product.xpath(".//a/@href").get()
        #     title = product.xpath(".//a/@title").get()
        #     category = product.xpath(".//a/@data-category").get()
        #     image = product.xpath(".//a[1]/span[1]/img/@src").get()
        #     brand = product.xpath(".//h4/text()").get()
        #     name = product.xpath(".//h3/a[2]/text()").get()
        #     old_price = product.xpath(".//p[@class='old-price']/span[2]/text()").get()
        #     current_price = product.xpath(".//p[@class='special-price']/span[2]/text()").get()

        #     yield{
        #         "product_name": name,
        #         "product_brand": brand,
        #         "product_link": link,
        #         "product_image": image,
        #         "product_category": category,
        #         "old_price": old_price,
        #         "special_price": current_price,
        #     }

        # next_page = response.xpath("(//a[@class='next i-next'])[2]/@href").get()
        # if next_page:
        #     yield scrapy.Request(url = next_page, callback=self.parse)
        
        

