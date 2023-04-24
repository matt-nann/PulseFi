
import sys
import os
sys.path.append('../..')

import asyncio
from playwright.async_api import async_playwright
# from src import getSecret
# Replace with your Google email and password
email = 'matpar481@gmail.com' 
# getSecret('GOOGLE_USERNAME')
password = 'HZe3w4hcVM!pU7#Gp6LN'
# getSecret('GOOGLE_PASSWORD')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Navigate to the URL
        url = 'https://myactivity.google.com/product/youtube'
        await page.goto(url)

        # Log in to your Google account
        await page.fill('//*[@id="identifierId"]', email)
        await page.press('//*[@id="identifierId"]', 'Enter')
        # await page.wait_for_timeout(2000)  # Wait for the password field to appear

        # await page.fill('//*[@id="password"]/div[1]/div/div[1]/input', password)
        # await page.press('//*[@id="password"]/div[1]/div/div[1]/input', 'Enter')
        # await page.wait_for_timeout(5000)  # Wait for the page to load

        # Get the page's HTML content
        html_content = await page.content()

        # Close the browser
        await browser.close()

        # Print the HTML content
        print(html_content)

asyncio.run(main())
