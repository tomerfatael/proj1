import sys
import urllib.parse
import re
import requests
import lxml.html
import rdflib
from urllib.parse import unquote

g = rdflib.Graph()
COUNTRIES = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
WIKI_PREFIX = "https://en.wikipedia.org"
EXAMPLE = "http://example.org/"
countries_url = []
countries_set = set()


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
        countries_set.add(country_name)
        ont_country = rdflib.URIRef(EXAMPLE + country_name)
        countries_url.append((url, ont_country))

def get_name_from_url(name):
    idx = name.find('wiki/')
    if idx != -1:
        name = name[idx+5:]
        return urllib.parse.unquote(name)

def get_place_of_birth(places_of_birth):
    place_of_birth = None
    for place in places_of_birth:
        if place in countries_set:
            place_of_birth = place
            break
    return place_of_birth


def build_country_president(country_doc, ont_country):
    """
    getting president name and crawling to his wikipedia page
    in order to get his date of birth and place of birth
    :rtype: None
    """
    PRESIDENT_OF = rdflib.URIRef(EXAMPLE + "president_of")
    res = country_doc.xpath("//table[contains(@class, 'infobox')]//tr[th//a[text()='President']]//*[contains(@class, 'infobox-data')]//@href") #TODO maybe switch the th in *
    # check if the country have a president
    if len(res) > 0:
        president_name_url = res[0]
        president_name = get_name_from_url(president_name_url)
        ont_name = rdflib.URIRef(EXAMPLE + president_name)
        g.add((ont_name, PRESIDENT_OF, ont_country))
        g.add((ont_name, rdflib.URIRef(EXAMPLE + "is"), rdflib.URIRef(EXAMPLE + f"president_of_{ont_country[len(EXAMPLE):]}")))

        presidnet_wiki_suffix = country_doc.xpath("//table[contains(@class, 'infobox')]//tr[th//a[text()='President']]//td//a//@href")
        presidnet_wiki_url = WIKI_PREFIX + presidnet_wiki_suffix[0]
        # crawling into the president wikipedia page
        r = requests.get(presidnet_wiki_url)
        president_doc = lxml.html.fromstring(r.content)
        president_date_of_birth = president_doc.xpath("//table//tr[th[text()='Born']]//span[@class='bday']//text()")
        if len(president_date_of_birth) > 0:
            DATE_OF_BIRTH = rdflib.URIRef(EXAMPLE + "date_of_birth")
            ont_date_of_birth = rdflib.URIRef(EXAMPLE + president_date_of_birth[0])
            g.add((ont_name, DATE_OF_BIRTH, ont_date_of_birth))

        res = president_doc.xpath("//table//tr[th[text()='Born']]//a//@href")
        if len(res) > 0:
            places_of_birth = [get_name_from_url(place) for place in res]
            place_of_birth = get_place_of_birth(places_of_birth)

            if place_of_birth == None:
                res = president_doc.xpath("//table//tr[th[text()='Born']]//td//text()") # TODO which text to take??
                for elem in res:
                    places_of_birth = elem.split()
                    place_of_birth = get_place_of_birth(places_of_birth)
                    if place_of_birth != None:
                        break

            if place_of_birth != None:
                PLACE_OF_BIRTH = rdflib.URIRef(EXAMPLE + "place_of_birth")
                ont_place_of_birth = rdflib.URIRef(EXAMPLE + place_of_birth)
                g.add((ont_name, PLACE_OF_BIRTH, ont_place_of_birth))


def build_country_prime_minister(country_doc, ont_country):
    """
    getting prime minister name and crawling to his wikipedia page
    in order to get his date of birth and place of birth
    :rtype: None
    """
    PRIME_MINISTER_OF = rdflib.URIRef(EXAMPLE + "prime_minister_of")
    res = country_doc.xpath("//table[contains(@class, 'infobox')]//tr[th//a[text()='Prime Minister']]//*[contains(@class, 'infobox-data')]//@href")
    # check if the country have a prime minister
    if len(res) > 0:
        prime_minister_name_url = res[0]
        prime_minister_name = get_name_from_url(prime_minister_name_url)
        ont_name = rdflib.URIRef(EXAMPLE + prime_minister_name)
        g.add((ont_name, PRIME_MINISTER_OF, ont_country))
        g.add((ont_name, rdflib.URIRef(EXAMPLE + "is"), rdflib.URIRef(EXAMPLE + f"prime_minister_of_{ont_country[len(EXAMPLE):]}")))

        prime_minister_wiki_suffix = country_doc.xpath("//table[contains(@class, 'infobox')]//tr[th//a[text()='Prime Minister']]//td//a//@href")
        prime_minister_wiki_url = WIKI_PREFIX + prime_minister_wiki_suffix[0]
        # crawling into the prime minister wikipedia page
        r = requests.get(prime_minister_wiki_url)
        prime_minister_doc = lxml.html.fromstring(r.content)
        prime_minister_date_of_birth = prime_minister_doc.xpath("//table//tr[th[text()='Born']]//span[@class='bday']//text()")
        if len(prime_minister_date_of_birth) > 0:
            DATE_OF_BIRTH = rdflib.URIRef(EXAMPLE + "date_of_birth")
            ont_date_of_birth = rdflib.URIRef(EXAMPLE + prime_minister_date_of_birth[0])
            g.add((ont_name, DATE_OF_BIRTH, ont_date_of_birth))

        res = prime_minister_doc.xpath("//table//tr[th[text()='Born']]//a//@href")
        if len(res) > 0:
            places_of_birth = [get_name_from_url(place) for place in res]
            place_of_birth = get_place_of_birth(places_of_birth)

            if place_of_birth == None:
                res = prime_minister_doc.xpath("//table//tr[th[text()='Born']]//td//text()")
                for elem in res:
                    places_of_birth = elem.split()
                    place_of_birth = get_place_of_birth(places_of_birth)
                    if place_of_birth != None:
                        break

            if place_of_birth != None:
                PLACE_OF_BIRTH = rdflib.URIRef(EXAMPLE + "place_of_birth")
                ont_place_of_birth = rdflib.URIRef(EXAMPLE + place_of_birth)
                g.add((ont_name, PLACE_OF_BIRTH, ont_place_of_birth))


def build_country_capital(country_doc, ont_country):
    capital = country_doc.xpath("//table[contains(@class,'infobox')]//tr[th/text()='Capital']//td//a/text()") # TODO remember to remove the _ sign
    if len(capital) > 0:
        capital = capital[0].replace(" ", "_")
        ont_capital = rdflib.URIRef(EXAMPLE + capital)
        relation_capital_of = rdflib.URIRef(EXAMPLE + "capital_of")  # TODO check if we need 2 arcs to both sides, country->capital or capital->city. this is capital->country relation
        g.add((ont_capital, relation_capital_of, ont_country))  # adding capital->country


def get_population(text_list: list):
    for text in text_list:
        text = text.replace(" ", "")
        if text.replace(",", "").isnumeric():
            return text


def build_country_population(country_doc, ont_country):
    index = "count(//table[contains(@class,'infobox')]//tr[th//text()='Population']/preceding-sibling::*) + 2"
    text_list = country_doc.xpath("//table[contains(@class,'infobox')]//tr[" + index + "]/td//text()")
    number = get_population(text_list)

    ont_population = rdflib.URIRef(EXAMPLE + number)
    relation = rdflib.URIRef(EXAMPLE + "population_size")
    g.add((ont_country, relation, ont_population))


def build_country_area(country_doc, ont_country):
    index = int(country_doc.xpath("count(//table[contains(@class,'infobox')]//tr[th//text()='Area ']/preceding-sibling::*)") + 2)
    if index == 2:
        index = int(country_doc.xpath("count(//table[contains(@class,'infobox')]//tr[th//text()='Area']/preceding-sibling::*)") + 2) # fixing, 'Area ' VS 'Area' issue
    area = str(country_doc.xpath("//table[contains(@class,'infobox')]//tr[" + str(index) + "]/td//text()")[0]).split()
    area = area[0] + "_km_squared" # TODO see if it is better to add the km and squared only with the final answer
    ont_area = rdflib.URIRef(EXAMPLE + area)
    relation = rdflib.URIRef(EXAMPLE + "area_size")
    g.add((ont_country, relation, ont_area))


def build_country_form_of_government(country_doc, ont_country):
    GOVERNMENT_IN = rdflib.URIRef(EXAMPLE + "government_in")
    res = country_doc.xpath("//table[contains(@class, 'infobox')]//tr[.//text()='Government']//td//@title") # TODO make sure its the title what they asked for
    form_of_government = [government for government in res if government[0].isalpha()]
    for i in range(len(form_of_government)):
        g.add((rdflib.URIRef(EXAMPLE + form_of_government[i].replace(" ", "_")), GOVERNMENT_IN, ont_country))


def build_country(country_doc, ont_country):
    build_country_president(country_doc, ont_country)
    build_country_prime_minister(country_doc, ont_country)
    build_country_capital(country_doc, ont_country)
    build_country_area(country_doc, ont_country)
    build_country_form_of_government(country_doc, ont_country)
    # build_country_population(country_doc, ont_country)


def get_country_from_question(question: str, substring: str, last_place: bool=True) -> str:
    # TODO check countries with 2 word name
    """
    return the country name from the question
    case 1 (default) - country is the last word in the question
    case 2 - country is the second last word in the question
    :rtype: str
    """
    idx = question.find(substring)+1
    if(last_place):
        return question[idx+len(substring):len(question)-1].replace(" ", "_")
    return question[idx+len(substring):len(question)-len(" born?")].replace(" ", "_")


def build_query(question: str) -> str:
    if question.find("president of") != -1:
        # TODO maybe put those 3 if's in a function of its own
        if question.find("Who") != -1:
            country = get_country_from_question(question, "of")
            query = f"?e <{EXAMPLE}president_of>  <{EXAMPLE + country}> ."
            return "select * where {" + query + "}"

        elif question.find("When") != -1:
            country = get_country_from_question(question, "of", False)
            query = f"?e <{EXAMPLE}president_of>  <{EXAMPLE + country}> ." + f"?e <{EXAMPLE}date_of_birth> ?p ."
            return "select ?p where {" + query + "}"

        else:
            country = get_country_from_question(question, "of", False)
            query = f"?e <{EXAMPLE}president_of>  <{EXAMPLE + country}> ." + f"?e <{EXAMPLE}place_of_birth> ?p ."
            return "select ?p where {" + query + "}"

    elif question.find("prime minister of") != -1:
        if question.find("Who") != -1:
            country = get_country_from_question(question, "of")
            query = f"?e <{EXAMPLE}prime_minister_of>  <{EXAMPLE + country}> ."
            return "select * where {" + query + "}"

        elif question.find("When") != -1:
            country = get_country_from_question(question, "of", False)
            query = f"?e <{EXAMPLE}prime_minister_of>  <{EXAMPLE + country}> ." + f"?e <{EXAMPLE}date_of_birth> ?p ."
            return "select ?p where {" + query + "}"

        else:
            country = get_country_from_question(question, "of", False)
            query = f"?e <{EXAMPLE}prime_minister_of>  <{EXAMPLE + country}> ." + f"?e <{EXAMPLE}place_of_birth> ?p ."
            return "select ?p where {" + query + "}"

    elif question.find("form of government") != -1:
        country = get_country_from_question(question, "in")
        query = f"?e <{EXAMPLE}government_in> <{EXAMPLE + country}> ."
        return "select * where {" + query + "} order by ?e"

    elif question.find("capital of") != -1:
        country = get_country_from_question(question, "of")
        query = f"?e <{EXAMPLE}capital_of>  <{EXAMPLE + country}> ."
        return "select * where {" + query + "}"

    elif question.find("area") != -1:
        country = get_country_from_question(question, "of")
        query = f"<{EXAMPLE + country}>  <{EXAMPLE}area_size> ?e."
        return "select * where {" + query + "}"

    elif question.find("population") != -1:
        country = get_country_from_question(question, "of")
        query = f"<{EXAMPLE + country}>  <{EXAMPLE}population_size> ?e."
        return "select * where {" + query + "}"

    elif question.find("Who is") != -1:
        name = question[7:len(question)-1].replace(" ", "_")
        query = f"<{EXAMPLE + name}> <{EXAMPLE}is> ?e ."
        return "select * where {" + query + "}"

    elif question.find("How many") != -1: # TODO count the answer
        #How many forms of government
        if question.find("are also") != -1:
            idx = question.find("are also")
            form1, form2 = question[9:idx-1].replace(" ", "_"), question[idx+9:len(question)-1].replace(" ", "_")
            query = f"<{EXAMPLE + form1}> <{EXAMPLE}government_in> ?c ." + f" <{EXAMPLE + form2}> <{EXAMPLE}government_in> ?c ."
            return "select * where {" + query + "}"
         
         # How many presidents
        else:
            country = get_country_from_question(question, "in")
            query = f"?c <{EXAMPLE}place_of_birth> <{EXAMPLE + country}> ."
            return "select * where {" + query + "}"

    elif question.find("all") != -1:
        substring = question.split()[-1].lower() # returns the last word in the question - needs to be the substring
        query = f"?capital <{EXAMPLE}capital_of> ?country . filter (contains(LCASE(STR(?capital)), '{substring}') )"
        return "select ?country where {" + query + "} order by ?country"

def answer(query_result, question = None): # TODO if the answer is None, return 0 instead
    if question == None:
        return [ans[19:].replace("_", " ") for ans, *_ in query_result]

    elif question == "How many":
        for ans, *_ in query_result:
            return len(ans[19:].replace("_", " "))

# if sys.argv[1] == 'create':
#     build_countries_url()
#     for country in countries_url:
#         ont_country = rdflib.URIRef(country[1])
#         r = requests.get(country[0])
#         country_doc = lxml.html.fromstring(r)
#         build_country(country_doc, ont_country)
#         g.serialize("ontology.nt", format="nt")


# if sys.argv[1] == 'question':


################## inputs #####################

# input for few country tests
# AVI relevant countries

build_countries_url()
# a = requests.get("https://en.wikipedia.org/wiki/Republic_of_Ireland")
# doc = lxml.html.fromstring(a.content)
# ont_country = rdflib.URIRef(EXAMPLE + "Republic_of_Ireland")
# build_country_president(doc, ont_country)
# g.serialize("ontology.nt", format="nt")
# a = "Who is the prime minister of Eswatini?"
# b = build_query(a)
# g.parse("ontology.nt", format="nt")
# query_list_result = g.query(b)
# list = list(query_list_result)
# print(list)

# lst = ["China", "Portugal", "Guam", "Eswatini", "Tonga", "Argentina", "Sweden", "Bahrain", "North_Macedonia", "Iceland", "Fiji", "United_States", "Lesotho", "Indonesia", "Uruguay", "Solomon_Islands", "Lesotho", "Marshall_Islands", "Republic_of_the_Congo", "Republic_of_Ireland"]
# for country in lst:
#     country = country.replace(" ", "_")
#     r = requests.get("https://en.wikipedia.org/wiki/" + country)
#     doc = lxml.html.fromstring(r.content)
#     ont_country = rdflib.URIRef(EXAMPLE + country)
#     build_country(doc, ont_country)
# g.serialize("ontology.nt", format="nt")

a = "When was the president of United States born?"
b = build_query(a)
g.parse("ontology.nt", format="nt")
query_list_result = g.query(b)
c = answer(query_list_result)
print(c)

#input for all countries test

# build_countries_url()
# for c in countries_url:
#     ont_name = rdflib.URIRef(c[1])
#     a = requests.get(c[0])
#     doc = lxml.html.fromstring(a.content)
#     build_country_form_of_government(doc,ont_name)
# g.serialize("ontology.nt", format="nt")
# a = "How many Dictatorship are also Presidential system?"
# b = build_query(a)
# g.parse("ontology.nt", format="nt")
# query_list_result = g.query(b)
# list = list(query_list_result)

# TODO AVI: add order by to all queries which could have more than 1 answer - say to Tomer.
# TODO Avi: Saint_Helena,_Ascension_and_Tristan_da_Cunha name needs to dealt with. - ask in the forum
# TODO check about the relation from the pdf
# TODO Avi: ask Adam about COUNT is SPARQL queries
# TODO - make sure that in Republic of Ireland case, g should not include the place_of_birth relation (because the president place of birth is Ireland)
