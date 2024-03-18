from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse

@dataclass
class Business:
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    
#below code helps us to save the scraped data in excel and csv type 
@dataclass
class BusinessList:
    business_list: list[Business] = field(default_factory=list)    
    def dataframe(self):
            return pd.json_normalize((asdict(business) for business in self.business_list), sep='')
    
    def save_to_excel(self, filename):
            self.dataframe().to_excel(f'{filename}.xlsx', index=False)
        
    def save_to_csv(self, filename):
            self.dataframe().to_csv(f'{filename}.csv', index=False)


def main():
        #to automate the browser
        with sync_playwright() as p:
                browser = p.chromium.launch() #headless = False because in development mode, but in production you can avoid it because by default it is true
                page = browser.new_page()
                
                page.goto('https://www.google.com/maps', timeout=60000)
                page.wait_for_timeout(5000) # because od dev mode i give timeout=5000, but in production you can give it 1
                
                page.locator('//input[@id="searchboxinput"]').fill(search_for)
                page.wait_for_timeout(3000)
                
                page.keyboard.press('Enter')
                page.wait_for_timeout(5000)
                
                listings = page.locator('//div[@role = "article"]').all()
                print(len(listings))
                
                business_list = BusinessList()
                
                for listing in listings[:5]:
                        
                        listing.click()
                        page.wait_for_timeout(5000)
                        
                        name_xpath = '//h1[contains(@class, "fontHeadlineLarge")]/span[2]'
                        address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                        website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                        phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                        # review_count_xpath = '//button[@jsaction="pane.reviewChart.moreReviews"]//span'
                        # reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'
                        
                        business = Business()
                        business.name = page.locator(name_xpath).inner_text()
                        business.address = page.locator(address_xpath).inner_text()
                        business.website = page.locator(website_xpath).inner_text()
                        business.phone_number = page.locator(phone_number_xpath).inner_text()
                        
                        business_list.business_list.append(business) #passing adding the values
                business_list.save_to_excel('google_maps_data')
                business_list.save_to_csv('google_maps_data')
                
                browser.close()
                
#the below code/class allows to enter an input/command on the command line
if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--search", type=str)
        parser.add_argument("-l", "--location", type=str)
        args = parser.parse_args()

        if args.location and args.search:
                search_for = f'{args.search}  {args.location}'
        else:
                search_for = args.search if args.search else 'dentist new york'
        main()