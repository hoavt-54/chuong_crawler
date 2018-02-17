
# -*- coding: utf-8 -*-
###crawler muaban.net ###
###Prerequisite
# requests
# BeautifulSoup
#sdt, address, gia, description, image
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time, sys, os





### you may have to modify these configs

MainSite            = "https://muaban.net/mua-ban-nha-dat-cho-thue-toan-quoc-l0-c3"
PostSelectorOnMainSite  = ".mbn-box-list .mbn-box-list-content"
DateFormat          = "%d/%m/%Y"
PhotosSelectorInFullPage    = ".ct-image .item img[src$=jpg], .ct-image .item img[data-src$=jpg]"
PhoneNumberSelector = ".dt-content .ct-contact div b"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"
FAIL_ENCODING = 'ISO-8859-1'


SEND_ACC_ID = "login_name_of_sending_acc"
SEND_ACC_PASS = "login_password_of_sending_acc"
RECEIVE_ID = "chat_id_of_receiving_acc"









def get_html(url):
    #response = requests.get(
    #            url=url, **get_request_kwargs(timeout, useragent, proxies, headers))
    headers = {
                'User-Agent': USER_AGENT
            }
    response = requests.get(url=url, headers=headers)

    html = _get_html_from_response(response)
    return html



def get_request_kwargs(timeout, useragent, proxies, headers):
    """This Wrapper method exists b/c some values in req_kwargs dict
    are methods which need to be called every time we make a request
    """
    return {
        'headers': headers if headers else {'User-Agent': useragent},
        'cookies': cj(),
        'timeout': timeout,
        'allow_redirects': True,
        'proxies': proxies
    }



def _get_html_from_response(response):
    if response.encoding != FAIL_ENCODING:
        # return response as a unicode string
        html = response.text
    else:
        html = response.content
        if 'charset' not in response.headers.get('content-type'):
            encodings = requests.utils.get_encodings_from_content(response.text)
            if len(encodings) > 0:
                response.encoding = encodings[0]
                html = response.text

    return html or ''





"""
covert time string to unix timestamp
"""
def convert_string_date(sdate):
    datetime_object = datetime.strptime(sdate,DateFormat)
    if datetime_object:
        return time.mktime(datetime_object.timetuple())






"""
This method read images and phone number from the full post page
"""
def read_post_details(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    imgs, phone  = [], ""
    
    #get set of photos
    for itag in soup.select(PhotosSelectorInFullPage):
        if itag['data-src']:
            imgs.append(itag['data-src'])
            #print itag['data-src']
        else:
            #print itag['src']
            imgs.append(itag['src'])

    #get phone number
    phone= soup.select(".dt-content .ct-contact div b")
    if phone: phone = phone[0].text

    return imgs, phone

def send_message(fbclient, uid, title, timestring, summary, price, phone, address, images):
    message =  timestring 
    message += "\n--" + title + "--" 
    message += "\n\n#Mô tả: ".decode('utf-8')  + summary
    message += "\n\n#Địa chỉ: ".decode('utf-8')  + address
    message += "\n#Giá: ".decode('utf-8')  + price
    message += "\n#Điện thoại: ".decode('utf-8') + phone

    fbclient.sendRemoteImages(images, thread_id=uid, message=message) 

def read_history ():
    if not os.path.isfile("history.txt"): return {}
    hist={}
    with open("history.txt", "r") as f:
        for line in f:
            url, timestamp = line.strip().split()
            hist[url] = long(timestamp)

    return hist

def dump_history (hist):
    with open("history.txt", "w") as f:
        for url in hist:
            timestapm = hist[url]
            if timestapm < time.time() - 5 * 86400: continue # discard old urls
            f.write(url + "\t" + str(timestapm) + "\n")
if __name__ == '__main__':
    sys.path.insert(0, "./fbchat")
    from fbchat import client
    html = get_html(MainSite)
    soup = BeautifulSoup(html, 'html.parser')
    fb_client = client.Client(SEND_ACC_ID, SEND_ACC_PASS)
    hist = read_history()
    try:
        for post in soup.select(PostSelectorOnMainSite):
            try:
                time.sleep(10)
                title = post.select(".mbn-title")[0].text
                timestring = post.select(".mbn-date")[0].text
                summary = post.select(".mbn-item-summary")[0].text
                price = post.select(".mbn-price")[0].text
                address = post.select(".mbn-address")[0].text
                timestamp = convert_string_date(timestring)
                url = post.select("a[href^=https://muaban]")[0]['href']
                if url in hist: 
                    print ('parsed: ', url)
                    continue
                print ('parsing: ', url)
                hist[url] = long(timestamp)
                images, phone = read_post_details(url)
                send_message(fb_client, RECEIVE_ID, title, timestring, summary, price, phone, address, images)
            except:
                pass
    except:
        pass

    dump_history(hist)


