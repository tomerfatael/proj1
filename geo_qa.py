import requests
import lxml.html
import rdflib

g = rdflib.Graph()
COUNTRIES = " https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
WIKI_PREFIX =  "https://en.wikipedia.org"
countries_url = []


## building ontology ##

def build_countries_url():
    r = requests.get(COUNTRIES)
    doc = lxml.html.fromstring(r.content)
    for country in doc.xpath("//table//tbody//tr//span//a//@href"):
        url = WIKI_PREFIX + country
        countries_url.append(url)

def build_country_president(country_doc):
    # inserting president name to the graph
    president = country_doc.xpath("//table[contains(@class, 'infobox')]//tr[th//a[text()='President']]//td//a[@title][1]//text()")
    # check if the country have a president
    if(len(president) > 0):
        president_name = president[0]
        presidnet_wiki = country_doc.xpath("//table[contains(@class, 'infobox')]//tr[th//a[text()='President']]//td//a//@href")
        presidnet_wiki_url = WIKI_PREFIX + presidnet_wiki[0]
        # crawling into the president wikipedia page
        r = requests.get(presidnet_wiki_url)
        president_doc = lxml.html.fromstring(r.content)
        president_date_of_birth = president_doc.xpath("//table//tr[th[text()='Born']]//span[@class='bday']//text()") #returns the bday as a list
        president_place_of_birth = president_doc.xpath()

        # g.add()
        # g.add()

# input for tests
a = requests.get("https://en.wikipedia.org/wiki/china")
doc = lxml.html.fromstring(a.content)
build_country_president(doc)