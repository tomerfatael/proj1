
import requests
import lxml.html
import rdflib

g = rdflib.Graph()
COUNTRIES = " https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
countries_url = []


## building ontology ##

def get_countries_url():
    r = requests.get(COUNTRIES)
    doc = lxml.html.fromstring(r.content)
    for country in doc.xpath("//table//tbody//tr//span//a//@href"):
        url = "https://en.wikipedia.org" + country
        countries_url.append(url)


# def get_country_president(country_doc):
