from flask import Flask, render_template, redirect
import pymongo
from splinter import Browser
import time
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Instantiate Flask app
app = Flask(__name__)

# Connect to MongoDB
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# Connect to mars_app database
db = client.mars_app

# Connect to mars collection
mars_coll = db.mars

@app.route('/')
def index():

    mars_data = mars_coll.find_one()

    return(render_template('index.html', mars_data=mars_data))

@app.route('/scrape')
def scrape():

    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    # this is the py script with all of the scraping functions
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    time.sleep(1)
    html = browser.html
    soup = bs(html, "html.parser")
    first_slide = soup.find("li", class_="slide")
    news_title = first_slide.find("div", class_="content_title").get_text()
    news_p = first_slide.find("div", class_="article_teaser_body").get_text()


    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    time.sleep(3)
    image_link = browser.find_by_css('img[class="BaseImage  object-contain"]')
    image_link.click()
    time.sleep(3)
    image_link = browser.find_by_css('svg[class="IconExpand"]')
    image_link.click()
    time.sleep(3)
    html = browser.html
    soup = bs(html, 'html.parser')
    image = soup.find('div', class_='BaseLightbox__slide__img')
    featured_image_url = image.img['src']


    url ="https://space-facts.com/mars/"
    tables = pd.read_html(url)
    mars_facts = tables[0]
    mars_facts.columns=['Feature', 'Data']
    mars_facts.set_index('Feature', inplace=True)
    mars_facts_html = mars_facts.to_html(classes='table table-striped', index=True, border=0)


    url ="https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    hemisphere_image_urls = []
    links = browser.find_by_css("a.product-item h3")
    for i in range(len(links)):
        
        hemisphere = {}
        browser.find_by_css("a.product-item h3")[i].click()
        sample = browser.links.find_by_text('Sample').first
        hemisphere['img_url'] = sample['href']
        hemisphere['title'] = browser.find_by_css("h2.title").text
        hemisphere_image_urls.append(hemisphere)
        browser.back()

    browser.quit()


    # Gather document to insert
    nasa_document = {
        'news_title': news_title,
        'news_paragraph': news_p,
        'featured_img_url': featured_image_url,
        'mars_facts_html': mars_facts_html,
    }

    # Insert into the mars collection
    # mars_coll.insert_one(nasa_document)

    # Upsert into the mars collection (preferred to avoid duplicates)
    mars_coll.update_one({}, {'$set': nasa_document}, upsert=True)

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)