from django.http import HttpResponse
from django.shortcuts import render
import requests
from requests_html import HTMLSession
import urllib
# Create your views here.

def get_source(url):
    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)

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


def get_results(query):

    query = urllib.parse.quote_plus(query)
    response = get_source("https://www.google.co.uk/search?q=" + query)
    # replace whitespace with +
    query = query.replace(" ", "+")
    return response
def brave_results(query):
    query = urllib.parse.quote_plus(query)
    response2 = get_source("https://search.brave.com/search?q=" + query)
    # replace whitespace with +
    query = query.replace(" ", "+")
    return response2

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

    return output

def google_search(query):
    response = get_results(query)
    return parse_results(response)


# home function

def home(request):
    return render(request, 'core/home.html')

# brave search

def brave_search(response2):
    output2 = []
    results2 = response2.html.find('#side-right')
    for result2 in results2:
        data2 = dict()
        data2['title1'] = result2.find('.infobox-title', first=True).text
        data2['description'] = result2.find('.infobox-description', first=True).text
        data2['big_description'] = result2.find('.body .mb-6', first=True).text
        data2['links'] = result2.find('.links a', first=True).attrs['href']
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

            data2['image_url'] = response3.html.find('.infobox-image img')[0].attrs['src']

        except:
            pass
        output2.append(data2)
    return output2
# search function
def search_1(query):
    response2 = brave_results(query)
    return brave_search(response2)


def search(request):
    results = None
    brave__results = None
    if 'query' in request.GET:
        # Fetch search data
        query= request.GET['query']
        results= google_search(query)
        # Fetch brave data
        try:
            brave__results = search_1(query)
        except:
            pass
            
    # return render(request, 'core/search.html', {'data': results})
    return render(request, 'core/search.html', {'data': results, 'data2':brave__results})

# brave search 
