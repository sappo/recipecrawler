import re
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Identity

class Recipe(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    ingrediants = scrapy.Field()
    nutritions = scrapy.Field()

class RecipeLoader(ItemLoader):
    default_output_processor = TakeFirst()

    def parse_ingrediants(self, ingrediantNodes):
        ingrediants = []
        for ingrediantNode in ingrediantNodes:
            ingrediantParts = ingrediantNode.xpath("descendant::*[not(contains(@class, 'shoplink'))]/text()").extract()
            ingrediant = " ".join(part.strip() for part in ingrediantParts)
            ingrediant = re.sub(' +',' ',ingrediant)
            ingrediants.append(ingrediant)

        return ingrediants

    ingrediants_in = parse_ingrediants
    ingrediants_out = Identity()
