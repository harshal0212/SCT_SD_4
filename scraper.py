import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
SITE_URL = "https://books.toscrape.com/"

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


def fetch_page(page_number):
    url = BASE_URL.format(page_number)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch page {page_number}: {e}")


def parse_products(html):
    soup = BeautifulSoup(html, "lxml")
    product_cards = soup.select("article.product_pod")

    products = []
    for card in product_cards:
        name = card.h3.a.get("title", "").strip()

        price_text = card.select_one("p.price_color").get_text(strip=True)
        price_cleaned = price_text.replace("Â", "").replace("£", "").strip()
        try:
            price = float(price_cleaned)
        except ValueError:
            price = 0.0

        rating_class = card.select_one("p.star-rating").get("class", [])
        rating_word = next((c for c in rating_class if c != "star-rating"), "Zero")
        rating = RATING_MAP.get(rating_word, 0)

        availability = card.select_one("p.instock.availability")
        in_stock = "In stock" in availability.get_text(strip=True) if availability else False

        products.append({
            "Name": name,
            "Price (£)": price,
            "Rating": rating,
            "In Stock": "Yes" if in_stock else "No"
        })

    return products


def scrape_books(num_pages=1, progress_callback=None):
    all_products = []

    for page in range(1, num_pages + 1):
        if progress_callback:
            progress_callback(page, num_pages)

        html = fetch_page(page)
        products = parse_products(html)

        if not products:
            break

        all_products.extend(products)
        time.sleep(0.5)

    return all_products


if __name__ == "__main__":
    print("Testing scraper with 1 page...")
    data = scrape_books(num_pages=1)
    print(f"Scraped {len(data)} products")
    for product in data[:3]:
        print(product)