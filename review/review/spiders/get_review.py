import scrapy

from review.items import ReviewItem

class ReviewSpider(scrapy.Spider):
    name = "review"
    allowed_domains = ["goodreads.com"]
    start_urls = [
   "https://www.goodreads.com/book/show/34.The_Fellowship_of_the_Ring?from_search=true&search_version=service"
    ]

    def parse(self, response):
        for line in  response.xpath('//div[contains(@class, "updateActionLinks")]'):
          url = response.urljoin(line.xpath('a[last()]/@href').extract()[0])
          yield scrapy.Request(url, callback=self.get_text)
          
       # next_page = response.xpath('//div[contains(@class, "show-more")]/a/@href').extract()[0]
       # if (next_page != '#'):
       #     url = response.urljoin(next_page)
       #     yield scrapy.Request(url, self.parse)
            
    def get_text(self, response):
         item = ReviewItem()
         item['book'] = response.xpath('//a[contains(@class, "bookTitle")]/text()').extract()[0]
         item['user'] = response.xpath('//a[contains(@class, "userReview")]/text()').extract()[0]
         item['date'] = response.xpath('//span[contains(@itemprop, "publishDate")]/text()').extract()[0]
         item['likes'] = response.xpath('//span[contains(@class, "likesCount")]/text()').extract()[0].split()[0]
         item['stars'] = response.xpath('//a[contains(@class, "staticStars")]/text()').extract()[0].split()[0]
         body = response.xpath('//div[contains(@class, "big420BoxContent")]/div[contains(@class, "reviewText")]/text()').extract()
         text = ''
         for x in body:
             text = text + x
         item['text'] = text
         yield item