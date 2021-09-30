# UdemyBot - A Simple Udemy Free Courses Scrapper

# Copyright (C) 2021-Present Gautam Kumar <https://github.com/gautamajay52>


import asyncio
import json
from urllib.parse import unquote

import aiohttp
from bs4 import BeautifulSoup as bs
from yarl import URL

# this code/idea has taken from https://github.com/techtanic/Discounted-Udemy-Course-Enroller

class Scrapper:
    """Udemy Free Courses Scrapper"""

    def __init__(self) -> None:
        self.head = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }
        self.session = aiohttp.ClientSession

    async def __fetch_html(self, session: aiohttp.ClientSession, url) -> str:
        async with session.get(url) as response:
            return await response.text()

    async def __fetch_json(self, session: aiohttp.ClientSession, url) -> any:
        async with session.get(url) as response:
            return await response.json()

    async def __fetch_url(self, session: aiohttp.ClientSession, url) -> URL:
        async with session.get(url) as response:
            return response.url

    async def discudemy(self, page) -> list:
        du_links = []
        async with self.session(headers=self.head) as ass:
            soup = bs(
                await self.__fetch_html(
                    ass, "https://www.discudemy.com/all/" + str(page)
                ),
                "html5lib",
            )
            all = soup.find_all("section", "card")
            for index, items in enumerate(all):
                try:
                    title = items.a.text
                    url = items.a["href"]
                    soup = bs(await self.__fetch_html(ass, url), "html5lib")
                    next = soup.find("div", "ui center aligned basic segment")
                    url = next.a["href"]
                    soup = bs(await self.__fetch_html(ass, url), "html5lib")
                    du_links.append(
                        title + "|:|" + soup.find("div", "ui segment").a["href"]
                    )
                except AttributeError:
                    continue
            return self._parse(du_links)

    async def udemy_freebies(self, page) -> list:
        uf_links = []
        async with self.session(headers=self.head) as ass:
            soup = bs(
                await self.__fetch_html(
                    ass, "https://www.udemyfreebies.com/free-udemy-courses/" + str(page)
                ),
                "html5lib",
            )
            all = soup.find_all("div", "coupon-name")
            for index, items in enumerate(all):
                try:
                    title = items.a.text
                    url = items.a["href"]
                    soup = bs(await self.__fetch_html(ass, url), "html5lib")
                    next = soup.find("a", class_="button-icon")
                    url = next["href"]
                    uf_links.append(
                        title + "|:|" + str(await self.__fetch_url(ass, url))
                    )
                except AttributeError:
                    continue
        return self._parse(uf_links)

    async def tutorialbar(self, page) -> list:
        tb_links = []
        async with self.session(headers=self.head) as ass:
            soup = bs(
                await self.__fetch_html(
                    ass, "https://www.tutorialbar.com/all-courses/page/" + str(page)
                ),
                "html5lib",
            )
            all = soup.find_all(
                "div", class_="content_constructor pb0 pr20 pl20 mobilepadding"
            )
            for index, items in enumerate(all):
                title = items.a.text
                url = items.a["href"]
                soup = bs(await self.__fetch_html(ass, url), "html5lib")
                link = soup.find("a", class_="btn_offer_block re_track_btn")["href"]
                if "www.udemy.com" in link:
                    tb_links.append(title + "|:|" + link)
        return self._parse(tb_links)

    async def real_discount(self, page) -> list:
        rd_links = []
        async with self.session(headers=self.head) as ass:
            soup = bs(
                await self.__fetch_html(
                    ass, "https://app.real.discount/stores/Udemy?page=" + str(page)
                ),
                "html5lib",
            )
            all = soup.find_all("div", class_="col-xl-4 col-md-6")
            for index, items in enumerate(all):
                title = items.h3.text
                url = "https://app.real.discount" + items.a["href"]
                soup = bs(await self.__fetch_html(ass, url), "html5lib")
                try:
                    link = soup.select_one("a[href^='https://www.udemy.com']")["href"]
                    rd_links.append(title + "|:|" + link)
                except:
                    pass
        return self._parse(rd_links)

    async def coursevania(self) -> list:
        cv_links = []
        async with self.session(headers=self.head) as ass:
            soup = bs(
                await self.__fetch_html(ass, "https://coursevania.com/courses/"),
                "html5lib",
            )
            nonce = soup.find_all("script")[23].text
            nonce = json.loads(nonce.strip().strip(";").split('=')[1])["load_content"]
            url = (
                "https://coursevania.com/wp-admin/admin-ajax.php?&template=courses/grid&args={%22posts_per_page%22:%2230%22}&action=stm_lms_load_content&nonce="
                + nonce
                + "&sort=date_high"
            )
            r = await self.__fetch_json(ass, url)
            soup = bs(r["content"], "html5lib")
            all = soup.find_all(
                "div", attrs={"class": "stm_lms_courses__single--title"}
            )
            for index, items in enumerate(all):
                title = items.h5.text
                url = items.a["href"]
                soup = bs(await self.__fetch_html(ass, url), "html5lib")
                cv_links.append(
                    title
                    + "|:|"
                    + soup.find("div", attrs={"class": "stm-lms-buy-buttons"}).a["href"]
                )
        return self._parse(cv_links)

    async def idcoupons(self, page=1) -> list:
        idc_links = []
        async with self.session(headers=self.head) as ass:
            soup = bs(
                await self.__fetch_html(
                    ass,
                    "https://idownloadcoupon.com/product-category/udemy-2/page/"
                    + str(page),
                ),
                "html5lib",
            )
            all = soup.find_all("a", attrs={"class": "button product_type_external"})
            for index, items in enumerate(all):
                title = items["aria-label"]
                link = unquote(items["href"]).split("ulp=")
                try:
                    link = link[1]
                except IndexError:
                    link = link[0]
                if link.startswith("https://www.udemy.com"):
                    idc_links.append(title + "|:|" + link)
        return self._parse(idc_links)

    @staticmethod
    def _parse(links) -> list:
        if not links:
            return links
        _links = []
        r_links = []
        f_links = []
        n = 1
        for _link in links:
            link = _link.split("|:|")[1]
            title = _link.split("|:|")[0]
            lin = f"{n}) [{title}]({link})"
            _links.append(lin)
            if len(_links) == 20:
                f_links.append(_links)
                _links = []
                r_links = []
            else:
                r_links.append(lin)
            n += 1
        if r_links:
            f_links.append(r_links)

        return f_links
