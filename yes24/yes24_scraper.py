import requests
from bs4 import BeautifulSoup
import pandas as pd
from loguru import logger
import re
import os

# Logger configuration
logger.add("yes24_scraper.log", rotation="500 MB")

class Yes24Scraper:
    def __init__(self):
        self.base_url = "https://www.yes24.com/product/category/CategoryProductContents"
        self.headers = {
            "host": "www.yes24.com",
            "referer": "https://www.yes24.com/product/category/display/001001003032",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }
        self.params = {
            "dispNo": "001001003032",
            "order": "SINDEX_ONLY",
            "addOptionTp": "0",
            "page": "1",  # This will be updated in the loop
            "size": "24",
            "statGbYn": "N",
            "viewMode": "",
            "_options": "",
            "directDelvYn": "",
            "usedTp": "0",
            "elemNo": "0",
            "elemSeq": "0",
            "seriesNumber": "0"
        }
        self.all_books_data = []

    def _parse_book_item(self, item):
        """Parses a single book item (div.itemUnit) and extracts relevant information."""
        try:
            title_tag = item.select_one("div.item_info a.gd_name")
            title = title_tag.get_text(strip=True) if title_tag else "N/A"
            book_url = "https://www.yes24.com" + title_tag['href'] if title_tag and 'href' in title_tag.attrs else "N/A"
            
            author_tag = item.select_one("div.item_info span.info_auth a")
            author = author_tag.get_text(strip=True) if author_tag else "N/A"
            
            publisher_tag = item.select_one("div.item_info span.info_pub a")
            publisher = publisher_tag.get_text(strip=True) if publisher_tag else "N/A"
            
            pub_date_tag = item.select_one("div.item_info span.info_date")
            pub_date = pub_date_tag.get_text(strip=True) if pub_date_tag else "N/A"
            
            original_price_tag = item.select_one("div.item_info span.txt_num.dash em.yes_m")
            original_price = original_price_tag.get_text(strip=True).replace(",", "").replace("원", "") if original_price_tag else "N/A"
            
            discounted_price_tag = item.select_one("div.item_info strong.txt_num em.yes_b")
            discounted_price = discounted_price_tag.get_text(strip=True).replace(",", "").replace("원", "") if discounted_price_tag else "N/A"
            
            sales_index_tag = item.select_one("div.item_info span.saleNum")
            sales_index = re.search(r'\d+', sales_index_tag.get_text(strip=True)).group() if sales_index_tag and re.search(r'\d+', sales_index_tag.get_text(strip=True)) else "N/A"
            
            review_count_tag = item.select_one("div.item_info span.rating_rvCount em.txC_blue")
            review_count = re.search(r'\d+', review_count_tag.get_text(strip=True)).group() if review_count_tag and re.search(r'\d+', review_count_tag.get_text(strip=True)) else "0"
            
            rating_tag = item.select_one("div.item_info span.rating_grade em.yes_b")
            rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"
            
            tags = [tag.get_text(strip=True) for tag in item.select("div.info_row.info_tag span.tag a")]
            tags_str = ", ".join(tags)
            
            img_tag = item.select_one("div.item_img img.lazy")
            image_url = img_tag['data-original'] if img_tag and 'data-original' in img_tag.attrs else "N/A"

            return {
                "Title": title,
                "Book_URL": book_url,
                "Author": author,
                "Publisher": publisher,
                "Publication_Date": pub_date,
                "Original_Price": int(original_price) if original_price != "N/A" else None,
                "Discounted_Price": int(discounted_price) if discounted_price != "N/A" else None,
                "Sales_Index": int(sales_index) if sales_index != "N/A" else None,
                "Review_Count": int(review_count) if review_count != "N/A" else None,
                "Rating": float(rating) if rating != "N/A" else None,
                "Tags": tags_str,
                "Image_URL": image_url
            }
        except Exception as e:
            logger.error(f"Error parsing book item: {e}")
            return None

    def scrape_page(self, page_num):
        """Scrapes a single page of book listings."""
        self.params["page"] = str(page_num)
        logger.info(f"Scraping page {page_num}...")
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=self.params)
            response.raise_for_status() # Raise an exception for HTTP errors
            
            soup = BeautifulSoup(response.text, 'html.parser')
            book_items = soup.select("div.itemUnit")
            
            if not book_items:
                logger.info(f"No book items found on page {page_num}. Ending scrape.")
                return False

            for item in book_items:
                book_data = self._parse_book_item(item)
                if book_data:
                    self.all_books_data.append(book_data)
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for page {page_num}: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while scraping page {page_num}: {e}")
            return False

    def start_scraping(self, max_pages=5):
        """Starts the scraping process for multiple pages."""
        logger.info("Starting Yes24 scraping...")
        page = 1
        while page <= max_pages:
            if not self.scrape_page(page):
                break
            page += 1
            # Optional: Add a delay to avoid being blocked
            # import time
            # time.sleep(1) 
        logger.info(f"Finished scraping. Total books collected: {len(self.all_books_data)}")

    def save_to_csv(self, filename="yes24_ai.csv", directory="yes24/data"):
        """Saves the collected data to a CSV file."""
        if not self.all_books_data:
            logger.warning("No data to save.")
            return

        df = pd.DataFrame(self.all_books_data)
        os.makedirs(directory, exist_ok=True) # Ensure directory exists
        filepath = os.path.join(directory, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"Data successfully saved to {filepath}")

if __name__ == "__main__":
    scraper = Yes24Scraper()
    scraper.start_scraping(max_pages=3) # Scrape, for example, 3 pages
    scraper.save_to_csv()
