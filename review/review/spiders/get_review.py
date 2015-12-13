import scrapy

from review.items import ReviewItem

class ReviewSpider(scrapy.Spider):
    name = "review"
    allowed_domains = ["goodreads.com"]
    start_urls = [
       "https://www.goodreads.com/api/reviews_widget_iframe?did=i2WCQtEYsxMYHT8kGKzA&amp;format=html&amp;isbn=0618346252&amp;links=660&amp;min_rating=&amp;review_back=fff&amp;stars=000&amp;text=000"
    ]
    
    def parse(self, response):
        for line in response.xpath('//a[contains(@class, "gr_more_link")]'):
          url = line.xpath('@href').extract()[0]
          yield scrapy.Request(url, callback=self.get_text)
          
        next_page = response.xpath('//a[contains(@class, "next_page")]/@href').extract()[0]
        if (next_page != ''):
            url = response.urljoin(next_page)
            yield scrapy.Request(url, self.parse)
            
    def get_text(self, response):
         item = ReviewItem()
         item['book'] = response.xpath('//a[contains(@class, "bookTitle")]/text()').extract()[0]
         item['user'] = response.xpath('//a[contains(@class, "userReview")]/text()').extract()[0]
         item['date'] = response.xpath('//span[contains(@itemprop, "publishDate")]/text()').extract()[0]
         
         likes_temp = response.xpath('//span[contains(@class, "likesCount")]/text()').extract()
         if not likes_temp:
             item['likes'] = '0'
         else:
             item['likes'] = likes_temp[0].split()[0]
             
         stars_temp = response.xpath('//a[contains(@class, "staticStars")]/text()').extract()
         if not stars_temp:
             item['stars'] = '-1'
         else:
             item['stars'] = stars_temp[0].split()[0]
             
         body = response.xpath('//div[contains(@class, "big420BoxContent")]/div[contains(@class, "reviewText")]/text()').extract()
         text = ''
         for x in body:
             text = text + x
         item['text'] = text
         yield item
