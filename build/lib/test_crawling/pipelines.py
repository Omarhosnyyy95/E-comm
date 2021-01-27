# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector


class SqlDbPipeline:
    
    # def process_item(self, item, spider):
    #     return item


    # def open_spider(self, spider):
        # self.mydb = mysql.connector.connect(host='localhost', user='root', passwd="",  database="data_test")
        # self.cursor = self.mydb.cursor()


    def process_item(self, item, spider):
        # sql = "INSERT INTO `mortoglou`(`scraping_time`, `website_id`, `main_website_url`, `product_link`, `product_title`, `old_price`, `new_price`, `price`, `product_code`, `images`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # val = (item.get('scraping_time'), item.get('website_id'), item.get('main_website_url'), item.get('product_link'), item.get('product_title'), item.get('old_price'), item.get('new_price'), item.get('price'), item.get('product_code'), item.get('images'))
        # self.cursor.execute(sql, val)
        # self.mydb.commit()
        return item

    # def close_spider(self, spider):
    #     self.cursor.close()
    #     self.mydb.close()

# class TestCrawlingPipeline:
    
#     def open_spider(self, spider):
#         self.mydb = mysql.connector.connect(host='localhost', user='root', passwd="",  database="data_test")
#         self.cursor = self.mydb.cursor()


#     def process_item(self, item, spider):
#         #return item
#         sql = "INSERT INTO `websites`(`website_id`, `main_page_url`, `product_link`, `product_title`) VALUES (%s, %s, %s, %s)"
#         val = (item.get('website_id'), item.get('main_page_url'), item.get('link'), item.get('Title'))
#         self.cursor.execute(sql, val)
#         self.mydb.commit()

#     def close_spider(self, spider):
#         self.cursor.close()
#         self.mydb.close()