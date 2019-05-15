import urllib.request as urllib2
import json
import os
import ssl

from datetime import datetime
from threading import Timer
from bs4 import BeautifulSoup
import requests

class VakantieVeilingen:
    movie_rating = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }

    def login(self):
        login_data = {
            'login': '',
            'password': ''
        }

        session = requests.Session()
        url = "https://www.vakantieveilingen.be/login.html"

        session.post(url, data=login_data, headers=self.headers)
        return session

    def fetch_highest_price_from_product_page(self, session, url):

        request = requests.Request('GET', url, headers=self.headers)
        prepared_request = session.prepare_request(request)
        response = session.send(prepared_request, allow_redirects=False)

        soup = BeautifulSoup(response.content, 'html5lib')

        highest_bid = soup.find("span", {"id": "jsMainLotCurrentBid"}).text
        print(highest_bid)

        return int(highest_bid)

    def calculate_expiration_time(self, session, url):
        request = requests.Request('GET', url, headers=self.headers)
        prepared_request = session.prepare_request(request)
        response = session.send(prepared_request, allow_redirects=False)

        soup = BeautifulSoup(response.content, 'html5lib')
        lot_expire_time = soup.find("div", {"id": "biddingBlock"})["data-lot-expires"]
        print(lot_expire_time)
        return self.convert_string_date_to_timestamp(lot_expire_time)

    def schedule_bid(self, session, secs_to_expiration, product_page_url):
        t = Timer(secs_to_expiration, self.place_bid, [session, product_page_url])
        t.start()

    def place_bid(self, session, product_page_url):
        current_highest_bid = self.fetch_highest_price_from_product_page(session, product_page_url)
        my_highest_bid = 20
        if current_highest_bid + 1 < my_highest_bid:
            my_bid = current_highest_bid + 1
            print("will now place bid of: " + str(my_bid))
        else :
            print("highest bid was to high for me")

    def convert_string_date_to_timestamp(self, expire_date_time):
        formatted_expire_date_time = expire_date_time.replace("T", " ").split("+")[0]

        expire_date = datetime.strptime(formatted_expire_date_time, '%Y-%m-%d %H:%M:%S')
        seconds_to_lot_expiration= expire_date.timestamp() - datetime.now().timestamp() - 1
        print("Converted expiration expire_date to timestamp : " + str(expire_date.timestamp()))
        print("Seconds remaining to expiration : " + str(seconds_to_lot_expiration))

        return seconds_to_lot_expiration

vakantie_veilingen = VakantieVeilingen()
outer_session = vakantie_veilingen.login()
#product_page_url = "https://www.vakantieveilingen.be/producten/klussen/borenset-set_wolfgang-170-set.html"
outer_product_page_url = "https://www.vakantieveilingen.be/producten/koken-en-tafelen/keukenmachine_bh9042.html"

outer_secs_to_expiration = vakantie_veilingen.calculate_expiration_time(outer_session, outer_product_page_url)
vakantie_veilingen.schedule_bid(outer_session, outer_secs_to_expiration, outer_product_page_url)

