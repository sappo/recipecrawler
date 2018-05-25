import scrapy


class QuotesSpider(scrapy.Spider):
    name = "eatsmarter"

    def start_requests(self):
        # Spiders can be started with optional attributes via '-a attribute=value'
        # attribute = getattr(self, 'attribute', None)
        #   if attribute is not None:
        #       pass
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Yield'ed json can be saved with: scrapy crawl <spider> -o output.json
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }

        # Yield'ed scrapy.Requests follows other links
        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
            # Or
            # yield response.follow(next_page, callback=self.parse)
