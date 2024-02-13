import scrapy
from mal_manga.items import MalMangaItem


class MangaspiderSpider(scrapy.Spider):
    name = 'mangaspider'
    allowed_domains = ['myanimelist.net']
    start_urls = ['https://myanimelist.net/topmanga.php']

    # Deal with all items that require to scroll through all <a> tag to get the text, eg. key=Genre
    def left_a_tag_words(self, responsepath):
        if responsepath:
            cur_key = ''
            for key in responsepath:
                cur_key += str(key.get().strip()) + ','
            return cur_key
        else:
            return None
    
    def check_none(self, responsepath):
        if responsepath:
            return responsepath.get().strip()
        else:
            return None
    
    
    def parse(self, response):
        
        # Get link of all individual mangas
        manga_links = response.xpath("//a[@class='hoverinfo_trigger fl-l ml12 mr8']/@href")
        
        for manga in manga_links:
            yield response.follow(manga.get(), callback=self.parse_manga_homepage)
            # yield response.follow(manga.get()+'/stats', callback=self.parse_manga_stats)
        
        
        next_page = response.xpath("//div[@class='di-b ac pt16 pb16 pagination icon-top-ranking-page-bottom']/a[@class='link-blue-box next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    
    def parse_manga_homepage(self, response):
        
        manga_item = MalMangaItem()
        
        manga_item['Title'] = self.check_none(response.xpath("//span[@class='h1-title']/span[@itemprop='name']/text()"))
        manga_item['Type'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Type')]]/../a/text()"))
        manga_item['Volumes'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Volume')]]/../text()"))
        manga_item['Chapters'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Chapter')]]/../text()"))
        manga_item['Status'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Status')]]/../text()"))
        manga_item['Published'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Published')]]/../text()"))
        manga_item['Genres'] = self.left_a_tag_words(response.xpath(f"//span[@class='dark_text'][text()[contains(.,'Genre')]]/../a/text()"))
        manga_item['Themes'] = self.left_a_tag_words(response.xpath(f"//span[@class='dark_text'][text()[contains(.,'Theme')]]/../a/text()"))
        manga_item['Demographic'] = self.left_a_tag_words(response.xpath(f"//span[@class='dark_text'][text()[contains(.,'Demographic')]]/../a/text()"))
        manga_item['Authors'] = self.left_a_tag_words(response.xpath(f"//span[@class='dark_text'][text()[contains(.,'Author')]]/../a/text()"))
        
        manga_item['Score'] = self.check_none(response.xpath("//span[@itemprop='ratingValue']/text()"))
        manga_item['Ranked'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Rank')]]/../text()")[1])
        manga_item['Popularity'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Popularity')]]/../text()"))                      
        manga_item['Members'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Member')]]/../text()"))
        manga_item['Favorites'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Favorite')]]/../text()"))                        
        
        yield response.follow(response.url+'/stats', callback=self.parse_manga_stats, meta={'item':manga_item})
                
   
    def parse_manga_stats(self, response):
        
        manga_item = response.meta['item']
        
        manga_item['Reading'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Reading')]]/../text()"))
        manga_item['Completed'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Completed')]]/../text()"))
        manga_item['On_Hold'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'On-Hold')]]/../text()"))
        manga_item['Dropped'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Dropped')]]/../text()"))
        manga_item['Plan_to_Read'] = self.check_none(response.xpath("//span[@class='dark_text'][text()[contains(.,'Plan to Read')]]/../text()"))
        
        scores = response.xpath("//div[@class='updatesBar']/following-sibling::span/small/text()")
        if scores:
            for n, i in enumerate(scores):
                manga_item[f'Score_{10-n}'] = i.get().strip('()').split(' ')[0]
        else:
            for n in range(1,11):
                manga_item[f'Score_{n}'] = None
            
        yield manga_item
        
    
    
    
    
    
    
    
    
