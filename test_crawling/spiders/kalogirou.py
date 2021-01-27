import scrapy
from datetime import datetime


class KalogirouSpider(scrapy.Spider):
    name = 'kalogirou'
    allowed_domains = ['www.kalogirou.com']
    # start_urls = ['http://www.kalogirou.com/']

    def start_requests(self):
        
        # working with xpath for this website

        main_page_url = 'https://www.kalogirou.com/el/'
        categories = {
            'Women-Clothes': 'https://www.kalogirou.com/el/gynaikia/gynaikia-roucha.html', 
            'Women-Shoes': "https://www.kalogirou.com/el/gynaikia/gynaikia-papoutsia.html",
            'Women-Bags': "https://www.kalogirou.com/el/gynaikia/gynaikia-tsantes.html",
            'Women-Accessories': "https://www.kalogirou.com/el/gynaikia/gynaikia-axesouar.html",
            'Men-Clothes': 'https://www.kalogirou.com/el/antrika/antrika-roucha.html', 
            'Men-Shoes': 'https://www.kalogirou.com/el/antrika/antrika-papoutsia.html', 
            'Men-Bags': 'https://www.kalogirou.com/el/antrika/antrikes-tsantes.html', 
            'Men-Accessories': 'https://www.kalogirou.com/el/antrika/antrika-axesouar.html', 
            'Child-Boy': 'https://www.kalogirou.com/el/paidika/agori.html', 
            'Child-Girl': 'https://www.kalogirou.com/el/paidika/koritsi.html', 
            }
        
        products_sel = "//div[@class='product-item-info']"
        product_link_sel = ".//a[@class='product photo product-item-photo']/@href"
        product_image_sel = ".//a//img/@data-src"
        product_title_sel = ".//a//img/@alt"
        product_brand_sel = ".//strong[@class='product name product-item-name']/a/text()"
        product_code_sel = ".//a[@class='product photo product-item-photo']/@data-prod-img-id"
        old_price_sel = ".//div[@class='ns-actions-m loaded']//div[@class='price-box price-final_price']/span[@class='normal-price']//span[@class='price-wrapper ']//text()"
        new_price_sel = ".//div[@class='ns-actions-m loaded']//div[@class='price-box price-final_price']/span[@class='old-price sly-old-price no-display']//span[@class='price-wrapper ']//text()"
        price_sel = ".//div[@class='ns-actions-m loaded']//div[@class='price-box price-final_price']/span[@class='normal-price']//span[@class='price-wrapper ']//text()"
        next_page_sel = "//div[@class='pages']/ul/li/a[@class='action  next']/@href"
        # post_link_selector = ''
        # post_selector = 'a.product-img'
        # next_page_selector = "#top-pagination a.next"
        # post_title_selector = "h1"
        # product_meta = {'old_price': '.product-price-old', 'new_price': '.product-price-new', 'price': '.product-price', 'product_code': '.product-model span', 'images': '.swiper.main-image .swiper-container .swiper-wrapper > .swiper-slide:first-child img', 'brand': 'div.product-right div.custom-product-manufacturer-mobile a'}
        

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