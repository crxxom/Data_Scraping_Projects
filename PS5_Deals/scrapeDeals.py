from bs4 import BeautifulSoup
import requests
import tqdm
import pandas as pd
from datetime import datetime
import time
import logging

# logging config
stdout_file = "/Users/jadonng/Desktop/Computer_Science/Data_Scraping/PS5_Deals/stdout.log"
logging.basicConfig(filename=stdout_file, level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')

error_file = "/Users/jadonng/Desktop/Computer_Science/Data_Scraping/PS5_Deals/stderror.log"
logging.basicConfig(filename=error_file, level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] %(message)s')

# define class - use .return_dict() to return the object metadata
class DiscountedGame():
    def __init__(self, html):
        self.html = html
        self.link = self.get_link()
        self.pagehtml = self.get_pagehtml()
        self.title = self.get_title()
        self.publisher = self.get_publisher()
        self.discount_pct = self.get_discountpct()
        self.original_price = self.get_originalprice()
        self.discounted_price = self.get_discountedprice()
        self.discount_endtime = self.get_discountendtime()
        self.rating = self.get_rating()
        self.rating_num = self.get_ratingnum()
        # self.datetime = datetime.now().strftime('%d/%-m/%Y')
        self.genre = self.get_genre()
        self.releasedate = self.get_releasedate()
        
    def get_link(self):
        try:
            link = 'https://store.playstation.com' + self.html.find('a',{'class': 'psw-link'}).get('href')
        except:
            return None
        return link

    def get_pagehtml(self):
        try:
            url = self.link
            result = requests.get(url).text
            doc = BeautifulSoup(result, 'html.parser')
            return doc
        except:
            return None

    def get_title(self):
        try:
            title = self.pagehtml.find('h1',{'class': 'psw-t-title-l'}).text
        except:
            return None
        return title

    def get_publisher(self):
        try:
            publisher = self.pagehtml.find('div',{'data-qa': 'mfe-game-title#publisher'}).text
        except:
            return None
        return publisher

    def get_discountpct(self):
        try:
            discountpct = self.pagehtml.find('span',{'data-qa': 'mfeCtaMain#offer0#discountInfo'}).text.split()[-1]
        except:
            return None
        return discountpct

    def get_discountendtime(self):
        try:
            discountendtime = ' '.join(self.pagehtml.find('span',{'data-qa': 'mfeCtaMain#offer0#discountDescriptor'}).text.split()[2:])
        except:
            return None
        return discountendtime
        
    def get_originalprice(self):
        try:
            originalprice = self.pagehtml.find('span',{'data-qa': 'mfeCtaMain#offer0#originalPrice'}).text
        except:
            return None
        return originalprice

    def get_discountedprice(self):
        try:
            discountedprice = self.pagehtml.find('span',{'data-qa': 'mfeCtaMain#offer0#finalPrice'}).text
        except:
            return None
        return discountedprice

    def get_rating(self):
        try:
            rating = self.pagehtml.find('div',{'data-qa': 'mfe-game-title#average-rating'}).text
        except:
            return None
        return rating

    def get_ratingnum(self):
        try:
            ratingnum = self.pagehtml.find('div',{'data-qa': 'mfe-game-title#rating-count'}).text.split()[0]
        except:
            return None
        return ratingnum

    def get_genre(self):
        try:
            genre = self.pagehtml.find('dd',{'data-qa': 'gameInfo#releaseInformation#genre-value'}).text
        except:
            return None
        return genre
    def get_releasedate(self):
        try:
            release_date = self.pagehtml.find('dd',{'data-qa': 'gameInfo#releaseInformation#releaseDate-value'}).text
        except:
            return None
        return release_date
        
    def return_dict(self):
        dict_object = {
            'Title': self.title,
            'Publisher': self.publisher,
            'Link': self.link,
            'DiscountPCT': self.discount_pct,
            'OriginalPrice': self.original_price,
            'DiscountPrice': self.discounted_price,
            # 'Discount_Startdate': self.datetime,
            'Discount_Endtime': self.discount_endtime,
            'Rating': self.rating,
            'Rating_count': self.rating_num,
            'Genre': self.genre,
            'ReleaseDate': self.releasedate,
            
        }
        
        return dict_object

#==========================================================================================
# MAIN FUNCTION 
#==========================================================================================
page = 0
num_deals = 0
metadata = []
starttime = datetime.now()

try:
    # scrape all metadata 
    while True:
        print(page, end=' ')
        try:
            # scrape each page (24 games per page)
            url = f'https://store.playstation.com/en-hk/category/29696e1b-a942-4832-935d-ebd11b163263/{page}'
            result = requests.get(url).text
            doc = BeautifulSoup(result, 'html.parser')
            all_games = doc.find('ul',{'class':'psw-grid-list'}).find_all('li') # list containing parsed html of all 24 games
            
            # hit final page
            if len(all_games) <10 or page > 200:
                break
                
            # scrape content in each page
            for html in all_games:
                game_data = DiscountedGame(html).return_dict()
                metadata.append(game_data)
                num_deals += 1

        except: # scrape till the end of page
            break
        
        page += 1
    
    # load previous dataset, drop all duplicate entries
    
    new_deals_df = pd.DataFrame(metadata)
    all_deals_df = pd.read_csv('/Users/jadonng/Desktop/Computer_Science/Data_Scraping/PS5_Deals/historic_deals.csv')
    
    combined_df = pd.concat([new_deals_df, all_deals_df],axis=0)
    combined_df = combined_df.drop_duplicates(subset=['Title','DiscountPCT','Discount_Endtime'])
    combined_df.to_csv('/Users/jadonng/Desktop/Computer_Science/Data_Scraping/PS5_Deals/historic_deals.csv',index=False)

    # logging
    month_day_year = datetime.now().strftime("%d/%m/%Y")
    runtime = (datetime.now() - starttime).total_seconds()

    logging.info(f"{month_day_year}: Scraped {page} pages, {num_deals} games, script ran for {runtime} seconds")

except Exception as e:
    logging.error(str(e))
    
