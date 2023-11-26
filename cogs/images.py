import discord
from discord.ext import commands
from consts import *
# from google_images_search import GoogleImagesSearch
from bs4 import BeautifulSoup
import urllib.request
import random

from selenium import webdriver
import time
import requests
import shutil
import os
import base64

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")

user = os.getlogin()
driver = webdriver.Chrome(chrome_options=chrome_options)
sampleSize = 100
lastQuery = ""
SCROLL_PAUSE_TIME = 0.2

# gis = GoogleImagesSearch('AIzaSyDqCWhPzItDYEq5RrJu2FilCRknYIr9sj4', '49a0ce90ec040f86e')
#
# _search_params = {
#     'q': 'cat',
#     'num': 1
# }

class ImagesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        driver.maximize_window()

    @commands.command(name="dog")
    async def dogImg(self, ctx):
        image = getImage("dog")
        embedVar = discord.Embed(color=EMBED_COLOR)
        embedVar.add_field(name="Dog time", value="Have a dog:", inline=False)
        embedVar.set_image(url=image)
        await ctx.send(embed=embedVar)

    @commands.command(name="cat")
    async def catImg(self, ctx):
        image = getImage("cat")
        embedVar = discord.Embed(color=EMBED_COLOR)
        embedVar.add_field(name="Cat time", value="Have a cat:", inline=False)
        embedVar.set_image(url=image)
        await ctx.send(embed=embedVar)

    @commands.command(name="search", aliases=["s"])
    async def searchImg(self, ctx, *args):
        img = getImage(" ".join(args))
        embedVar = discord.Embed(color=EMBED_COLOR)
        embedVar.add_field(name="Custom search", value="Found an image:", inline=False)
        embedVar.set_image(url=img)
        await ctx.send(embed=embedVar)

# def getImage(query):
#     image_type="ActiOn"
#     query= query.split()
#     query='%20'.join(query)
#     url="https://imgur.com/search/relevance?q_type=jpg&q_all="+query+"&qs=thumbs"
#     header={'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Chrome/43.0.2357.134 Safari/537.36"
#     }
#     soup = get_soup(url,header)
#
#     links=[]
#     for div in soup.find_all("div",{"class":"post"}):
#         links.extend(div.find_all("img"))
#     image = random.choice(links).get("src")
#     image = image[0:len(image)-5]
#     image += ".jpg"
#     return image

def getImage(inp):
    global lastQuery
    if lastQuery.lower() != inp.lower():
        driver.get('https://www.google.com/search?q='+inp+'&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947')
        time.sleep(2)

        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(2):
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    lastQuery = inp

    imgNum = random.randint(1,sampleSize)
    print(imgNum)
    imgurl = driver.find_element_by_xpath('//div//div//div//div//div//div//div//div//div//div['+str(imgNum)+']//a[1]//div[1]//img[1]')
    webdriver.ActionChains(driver).move_to_element(imgurl).perform()
    imgurl.click()
    time.sleep(1)
    img = driver.find_element_by_xpath('//body/div[2]/c-wiz/div[3]/div[2]/div[3]/div/div/div[3]/div[2]/c-wiz/div[1]/div[1]/div/div[2]/a/img').get_attribute("src")
    return img

# def get_soup(url,header):
#     return BeautifulSoup(urllib.request.urlopen(urllib.request.Request(url,headers=header)),'html.parser')

def setup(bot):
    bot.add_cog(ImagesCog(bot))
