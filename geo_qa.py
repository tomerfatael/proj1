import sys
import requests
import lxml.html
import rdflib

g = rdflib.Graph()
COUNTRIES = " https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
WIKI_PREFIX = "https://en.wikipedia.org"
countries_url = []
government_forms_dict = {}


## building ontology ##

def build_countries_url() -> None:
    """
    Creating a list of tuples (country url, country name)
    from the given wikipedia page of all countries
    :rtype: None
    """
    r = requests.get(COUNTRIES)
    doc = lxml.html.fromstring(r.content)
    for country in doc.xpath("//table//tbody//tr//span//a//@href"):
        url = WIKI_PREFIX + country
        country_name = country.split("/")[2]
        ont_country = rdflib.URIRef(country_name)
        countries_url.append((url, ont_country))

def build_country_president(country_doc, ont_country):
    """
    getting president name and crawling to his wikipedia page
    in order to get his date of birth and place of birth
    :rtype: None
    """
    PRESIDENT_OF = rdflib.URIRef("president_of")
    president_name = country_doc.xpath("//table[contains(@class, 'infobox')]//tr[th//a[text()='President']]//td//a[@title][1]//text()")
    # check if the country have a president
    if len(president_name) > 0:
        ont_name = rdflib.URIRef(president_name[0].replace(" ", "_"))
        g.add((ont_name, PRESIDENT_OF, ont_country))

        presidnet_wiki_suffix = country_doc.xpath("//table[contains(@class, 'infobox')]//tr[th//a[text()='President']]//td//a//@href")
        presidnet_wiki_url = WIKI_PREFIX + presidnet_wiki_suffix[0]
        # crawling into the president wikipedia page
        r = requests.get(presidnet_wiki_url)
        president_doc = lxml.html.fromstring(r.content)
        president_date_of_birth = president_doc.xpath("//table//tr[th[text()='Born']]//span[@class='bday']//text()")
        if len(president_date_of_birth) > 0:
            DATE_OF_BIRTH = rdflib.URIRef("date_of_birth")
            ont_date_of_birth = rdflib.URIRef(president_date_of_birth[0])
            g.add((ont_name, DATE_OF_BIRTH, ont_date_of_birth))

        res = president_doc.xpath("//table//tr[th[text()='Born']]//a//text()")
        president_place_of_birth = [place.replace(" ", "_") for place in res if place[0].isalpha()]
        if len(president_place_of_birth) > 0:
            PLACE_OF_BIRTH = rdflib.URIRef("place_of_birth")
            ont_place_of_birth = rdflib.URIRef(",".join(president_place_of_birth))
            g.add((ont_name, PLACE_OF_BIRTH, ont_place_of_birth))

def build_country_prime_minister(country_doc, ont_country):
    """
    getting prime minister name and crawling to his wikipedia page
    in order to get his date of birth and place of birth
    :rtype: None
    """
    PRIME_MINISTER_OF = rdflib.URIRef("prime_minister_of")
    prime_minister_name = country_doc.xpath("//table[contains(@class, 'infobox')]//tr[th//a[text()='Prime Minister']]//td//a[@title][1]//text()")
    # check if the country have a prime minister
    if len(prime_minister_name) > 0:
        ont_name = rdflib.URIRef(prime_minister_name[0].replace(" ", "_"))
        g.add((ont_name, PRIME_MINISTER_OF, ont_country))

        prime_minister_wiki_suffix = country_doc.xpath("//table[contains(@class, 'infobox')]//tr[th//a[text()='Prime Minister']]//td//a//@href")
        prime_minister_wiki_url = WIKI_PREFIX + prime_minister_wiki_suffix[0]
        # crawling into the prime minister wikipedia page
        r = requests.get(prime_minister_wiki_url)
        prime_minister_doc = lxml.html.fromstring(r.content)
        prime_minister_date_of_birth = prime_minister_doc.xpath("//table//tr[th[text()='Born']]//span[@class='bday']//text()")
        if len(prime_minister_date_of_birth) > 0:
            DATE_OF_BIRTH = rdflib.URIRef("date_of_birth")
            ont_date_of_birth = rdflib.URIRef(prime_minister_date_of_birth[0])
            g.add((ont_name, DATE_OF_BIRTH, ont_date_of_birth))

        res = prime_minister_doc.xpath("//table//tr[th[text()='Born']]//a//text()")
        prime_minister_place_of_birth = [place.replace(" ", "_") for place in res if place[0].isalpha()]
        if len(prime_minister_place_of_birth) > 0:
            PLACE_OF_BIRTH = rdflib.URIRef("place_of_birth")
            ont_place_of_birth = rdflib.URIRef(",".join(prime_minister_place_of_birth))
            g.add((ont_name, PLACE_OF_BIRTH, ont_place_of_birth))

def build_country_capital(country_doc, country):
    capital = country_doc.xpath("//table[contains(@class,'infobox')]//tr[th/text()='Capital']/td/a/text()")
        # add to g


def get_population(text_list: list):
    for text in text_list:
        number = text.replace(",", "").replace(" ", "")
        if number.isnumeric():
            return text


def build_country_population(country_doc, country):
    index = int(country_doc.xpath("count(//table[contains(@class,'infobox')]//tr[th//text()='Population']/preceding-sibling::*)") + 2)
    text_list = country_doc.xpath("//table[contains(@class,'infobox')]//tr[" + str(index) + "]/td//text()")
    number = get_population(text_list)
    x = 5
    # add to g


def build_country_form_of_government(country_doc, ont_country):
    GOVERNMENT_IN = rdflib.URIRef("government_in")
    res = country_doc.xpath("//table[contains(@class, 'infobox')]//tr[.//a[text()='Government']]//td//text()")
    form_of_government = [government for government in res if government[0].isalpha()]
    for government in form_of_government:
        #add to dict

        g.add((rdflib.URIRef(government.replace(" ", "_")), GOVERNMENT_IN, ont_country))

if sys.argv[1] == 'create':
    build_countries_url()
    for country in countries_url:
        ont_country = rdflib.URIRef(country[1])
        r = requests.get(country[0])
        country_doc = lxml.html.fromstring(r)
        build_country_president(country_doc, ont_country)
        build_country_prime_minister(country_doc, ont_country)
        build_country_form_of_government(country_doc, ont_country)
        #add avi functions
        g.serialize("ontology.nt", format="nt")

# if sys.argv[1] == 'question':



# input for single country tests

a = requests.get("https://en.wikipedia.org/wiki/israel")
doc = lxml.html.fromstring(a.content)
ont_country = rdflib.URIRef("india")
build_country_president(doc, ont_country)
# g.serialize("ontology.nt", format="nt") #after this command u can see the ontology graph in the ontology.nt file


#input for all countries test

# build_countries_url()
# for c in countries_url:
#     ont_name = rdflib.URIRef(c[1])
#     a = requests.get(c[0])
#     doc = lxml.html.fromstring(a.content)
#     build_country_president(doc,ont_name)
# g.serialize("ontology.nt", format="nt")