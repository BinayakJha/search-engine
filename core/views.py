from django.http import HttpResponse
from django.shortcuts import render
import requests
from requests_html import HTMLSession
import urllib
# Create your views here.

# def search_google(query):
#     query = query.replace(" ", "+")
#     url = f'https://www.google.com/search?q={query}'
#     try:
#         session = HTMLSession()
#         response = session.get(url)
     
#     except requests.exceptions.RequestException as e:
#         print(e)
#     titles = response.html.find('.yuRUbf h3', first=True).text
#     link = response.html.find('.yuRUbf a', first=True).attrs['href']
#     text = response.html.find('.IsZvec', first=True).text
#     results = response.html.find('.tF2Cxc', first=True).text
#     output=[]
#     for result in results:
#        item = {
#            'title': titles,
#            'link': link,
#            'text': text,
#        }
#        output.append(item)
#     print(item)
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
        data['cite'] = result.find(css_identifier_cite, first=True).text
        output.append(data)
    return output

def google_search(query):
    response = get_results(query)
    return parse_results(response)

# home function

def home(request):
    if 'query' in request.GET:
        # Fetch search data
        query= request.GET.get('query')
        results = google_search(query)
        pass
    return render(request, 'core/home.html',{'data':results})