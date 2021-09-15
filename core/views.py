from django.http import HttpResponse, request
from django.shortcuts import render
import requests
from requests_html import HTMLSession
import urllib
import replit
# Create your views here.

# ------------------------------------------------------------------------------------
# Get the source from the url function
# ------------------------------------------------------------------------------------

def get_source(url):
    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)

# ------------------------------------------------------------------------------------
# Scraping Google Search
# ------------------------------------------------------------------------------------

def scrape_google(query):

    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)

    links = list(response.html.absolute_links)
    google_domains = ('https://www.google.',
                      'https://google.',
                      'https://webcache.googleusercontent.',
                      'http://webcache.googleusercontent.',
                      'https://policies.google.',
                      'https://support.google.',
                      'https://maps.google.')

    for url in links[:]:
        if url.startswith(google_domains):
            links.remove(url)
    return links

# ------------------------------------------------------------------------------------
# getting results from the search
# ------------------------------------------------------------------------------------

def get_results(query):

    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)
    # replace whitespace with +
    query = query.replace(" ", "+")
    return response

# ------------------------------------------------------------------------------------
# brave results
# ------------------------------------------------------------------------------------

def brave_results(query):
    query = urllib.parse.quote_plus(query)
    response2 = get_source("https://www.google.co.uk/search?q=" + query)
    # replace whitespace with +
    query = query.replace(" ", "+")
    return response2

# ------------------------------------------------------------------------------------
# parsing results 
# ------------------------------------------------------------------------------------

def parse_results(response):
    css_identifier_result = ".tF2Cxc"
    css_identifier_title = ".yuRUbf h3"
    css_identifier_link = ".yuRUbf a"
    css_identifier_text = ".IsZvec"
    css_identifier_cite = ".iUh30"
    # related search tab
    css_identifier_featured = ".GyAeWb"
    results = response.html.find(css_identifier_result)
    # related search tab

    output = []
    for result in results:
        data = dict()
        data['title'] = result.find(css_identifier_title, first=True).text
        data['link'] = result.find(css_identifier_link, first=True).attrs['href']
        data['favicon'] = "https://www.google.com/s2/favicons?sz=64&domain_url=" + data['link']
        data['text'] = result.find(css_identifier_text, first=True).text
        # data['text2'] = data['text'].replace("\n", "")
        # filter the links from the text
        data['text'] = data['text'].replace(data['link'], '')
        # cite functions
        data['cite'] = result.find(css_identifier_cite, first=True).text
        data['cite'] = data['cite'].replace("https://", "")
        data['cite'] = data['cite'].replace("http://", "")
        data['cite'] = data['cite'].replace("www.", "")
        # close cite functions
        # youtube video image url
        if "/watch?v" in data['link']:
            link3 = data['link'][32:]
            data['yt_url'] = f"https://i.ytimg.com/vi/{link3}/0.jpg"
        output.append(data)
    # data['featured_answer'] = people_also_ask.get_simple_answer('2+2')
    return output


# ------------------------------------------------------------------------------------
# dooing google search
# ------------------------------------------------------------------------------------

def google_search(query):
    response = get_results(query)
    return parse_results(response)

# ------------------------------------------------------------------------------------
# home function
# ------------------------------------------------------------------------------------

def home(request):
    return render(request, 'core/home.html')

# ------------------------------------------------------------------------------------
# brave search
# ------------------------------------------------------------------------------------

def brave_search(response2):
    output2 = []
    try:
        results2 = response2.html.find('.liYKde')
    except:
        results2 = response2.html.find('.osrp-blk')
    for result2 in results2:
        data2 = dict()
        try:
            data2['title1'] = result2.find('.qrShPb', first=True).text
        except:
            pass
        try:
            data2['description'] = result2.find('.wwUB2c', first=True).text
        except:
            pass
        try:
            data2['big_description'] = result2.find('.kno-rdesc', first=True).text
        except:
            pass
        try:
            data2['links'] = result2.find('.osrp-blk', first=True).attrs['href']
        except:
            pass
        try:
            data2['rating'] = result2.find('.h6', first=True).text
            data2['rating_image'] = result2.find('.rating-source', first=True).attrs['src']
            data2['rating_text'] = result2.find('.r .flex-hcenter .text-sm', first=True).text
        except:
            pass
         # wikipedia image scraping
        try:
            # image
            img_url = data2['links']

            try:
                session = HTMLSession()
                response3 = session.get(img_url)

            except requests.exceptions.RequestException as e:
                print(e)
            try:
                data2['image_url'] = response3.html.find('.infobox-image img')[0].attrs['src']
            except:
                data2['image_url'] = response3.html.find('.thumbinner img')[0].attrs['src']
        except:
            pass
        output2.append(data2)
    return output2

# ------------------------------------------------------------------------------------
# brave search function
# ------------------------------------------------------------------------------------

def search_1(query):
    response2 = brave_results(query)
    return brave_search(response2)

# ------------------------------------------------------------------------------------
# main search function
# ------------------------------------------------------------------------------------

def search(request):
    results = None
    brave__results = None
    if 'query' in request.GET:
        # Fetch search data
        query= request.GET['query']
        results= google_search(query)

        # Fetch brave data
        brave__results = search_1(query)
    replit.clear()
    return render(request, 'core/search.html', {'data': results, 'data2':brave__results})
    
# ------------------------------------------------------------------------------------
# 
# ------------------------------------------------------------------------------------
