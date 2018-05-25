import re
import scrapy
from scrapy.linkextractors import LinkExtractor
from .recipe import Recipe, RecipeLoader

class EatsmarterSpider(scrapy.Spider):
    name = 'eatsmarter.de'
    allowed_domains = ['eatsmarter.de']
    start_urls = ['https://eatsmarter.de/rezepte/vegetarische-nudelpfanne']
    le = LinkExtractor(allow=('\/rezepte\/[^\/#?&]+(?=$)'),
                       allow_domains=allowed_domains)
    crawled_urls = set()

    def parse_nutrition_type_unit(self, type):
        unit = ''
        if type.find('/') > -1:
            # Drop Unit
            partition = type.rpartition('/')
            type = partition[0]
            unit = partition[2]

        if type == 'Ballaststoffe':
            type = 'Dietary Fiber'
        if type == 'BE':
            type = 'Bread Unit'
        if type == 'Brennwert':
            type = 'Calories'
        if type == 'Cholesterin':
            type = 'Cholesterol'
        if type == 'Eiweiß/Protein':
            type = 'Protein'
        if type == 'Eisen':
            type = 'Iron'
        if type == 'Fett':
            type = 'Total Fat'
        if type == 'Folsäure':
            type = 'Folic Acid'
        if type == 'Harnsäure':
            type = 'Uric Acid'
        if type == 'gesättigte Fettsäuren':
            type = 'Saturated Fat'
        if type == 'Jod':
            type = 'Iodine'
        if type == 'Kohlenhydrate':
            type = 'Total Carbohydrate'
        if type == 'Kallium':
            type = 'Potassium'
        if type == 'Kalzium':
            type = 'Calcium'
        if type == 'Pantothensäure':
            type = 'Pantothenic Acid'
        if type == 'zugesetzter Zucker':
            type = 'Sugars'
        if type == 'Zink':
            type = 'Zinc'

        return (type, unit)

    def parse(self, response):
        if response.css('.recipe-top'):
            self.logger.info('Hi, this is an item page! %s', response.url)
            recipe = RecipeLoader(item=Recipe(), response=response)
            recipe.add_value('url', response.url)
            recipe.add_xpath('title', "//*[@class='fn title p-name']/text()")
            recipe.add_value('ingrediants', response.xpath("//*[contains(@class, 'ingredients')]//*[contains(@class, 'ingredient')]"))
            yield response.follow(response.url + '/foodcheck#recipe-tabs',
                                  callback=self.parse_nutritions,
                                  meta={'recipe':recipe})

        for link in (link for link in self.le.extract_links(response) if link.url not in self.crawled_urls):
            self.crawled_urls.add(link.url)
            yield scrapy.Request(link.url, callback=self.parse)

    def parse_nutritions(self, response):
        nutritions = {}
        for nutritionNode in response.xpath("//*[contains(@class,'nutritions-table')]//tr"):
            tdNodes = nutritionNode.xpath("descendant::td/text()").extract()
            type_unit = tdNodes[0]
            value = tdNodes[1]
            type_unit = self.parse_nutrition_type_unit(type_unit)
            nutritions[type_unit[0]] = {'Unit': type_unit[1], 'Value:': value}

        recipe = response.meta['recipe']
        recipe.add_value('nutritions', nutritions)

        yield recipe.load_item()
