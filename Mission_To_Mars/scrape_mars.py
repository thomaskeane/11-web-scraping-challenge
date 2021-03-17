
from splinter import Browser
import time
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=False)

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
mars_facts.to_html()


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





