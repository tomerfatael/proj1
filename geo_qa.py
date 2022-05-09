import sys
import urllib.parse
import requests
import lxml.html
import rdflib


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
        country_name = get_name_from_url(country)
        countries_set.add(country_name)
        ont_country = rdflib.URIRef(EXAMPLE + country_name)
        countries_url.append((url, ont_country))


def get_name_from_url(name):
    idx = name.find('wiki/')
    if idx != -1:
        name = name[idx + 5:]
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
    res = country_doc.xpath(
        "//table[contains(@class, 'infobox')]//tr[th//a[text()='President']]//*[contains(@class, 'infobox-data')]//@href")  # TODO maybe switch the th in *
    # check if the country have a president
    if len(res) > 0:
        president_name_url = res[0]
        president_name = get_name_from_url(president_name_url)
        ont_name = rdflib.URIRef(EXAMPLE + president_name)
        g.add((ont_name, PRESIDENT_OF, ont_country))
        g.add((ont_name, rdflib.URIRef(EXAMPLE + "is"),
               rdflib.URIRef(EXAMPLE + f"President_of_{ont_country[len(EXAMPLE):]}")))

        presidnet_wiki_suffix = country_doc.xpath(
            "//table[contains(@class, 'infobox')]//tr[th//a[text()='President']]//td//a//@href")
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
                res = president_doc.xpath("//table//tr[th[text()='Born']]//td//text()")  # TODO which text to take??
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
    res = country_doc.xpath(
        "//table[contains(@class, 'infobox')]//tr[th//a[text()='Prime Minister']]//*[contains(@class, 'infobox-data')]//@href")
    # check if the country have a prime minister
    if len(res) > 0:
        if("Bahamas" not in ont_country):
            prime_minister_name_url = res[0]
            prime_minister_name = get_name_from_url(prime_minister_name_url)
        else:
            prime_minister_name = "Philip_Davis"

        ont_name = rdflib.URIRef(EXAMPLE + prime_minister_name)
        g.add((ont_name, PRIME_MINISTER_OF, ont_country))
        g.add((ont_name, rdflib.URIRef(EXAMPLE + "is"),
               rdflib.URIRef(EXAMPLE + f"Prime_Minister_of_{ont_country[len(EXAMPLE):]}")))

        prime_minister_wiki_suffix = country_doc.xpath(
            "//table[contains(@class, 'infobox')]//tr[th//a[text()='Prime Minister']]//td//a//@href")
        prime_minister_wiki_url = WIKI_PREFIX + prime_minister_wiki_suffix[0]
        # crawling into the prime minister wikipedia page
        r = requests.get(prime_minister_wiki_url)
        prime_minister_doc = lxml.html.fromstring(r.content)
        prime_minister_date_of_birth = prime_minister_doc.xpath(
            "//table//tr[th[text()='Born']]//span[@class='bday']//text()")
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
    capital = country_doc.xpath(
        "//table[contains(@class,'infobox')]//tr[th/text()='Capital']//td[not(text()='None')]//a//@href")
    if len(capital) > 0:
        capital = get_name_from_url(capital[0])
        capital = capital.replace(" ", "_")
        ont_capital = rdflib.URIRef(EXAMPLE + capital)
        relation_capital_of = rdflib.URIRef(EXAMPLE + "capital_of")
        g.add((ont_capital, relation_capital_of, ont_country))  # adding capital->country


def get_population(text_list: list):
    for text in text_list:
        idx = text.find("(")
        text2 = text
        if idx != -1:
            text = text[: idx]
        text = text.replace(" ", "")

        if text.replace(",", "").replace(".", "").isnumeric():
            return text

        if text2.find("or") != -1 or text2.find("million") != -1:
            return text2.replace(" ", "_") # made for Maldives


def build_country_population(country_doc, ont_country):
    # print(str(ont_country[19:]))  # TODO DELETE
    index = "count(//table[contains(@class,'infobox')]//tr[th//text()='Population']/preceding-sibling::*) + 2"
    text_list = country_doc.xpath("//table[contains(@class,'infobox')]//tr[" + index + "]/td//text()")
    number = get_population(text_list)
    # print(str(ont_country[19:]) + " " + number) #TODO DELETE

    ont_population = rdflib.URIRef(EXAMPLE + number)
    relation = rdflib.URIRef(EXAMPLE + "population_size")
    g.add((ont_country, relation, ont_population))
   # print("country: " + str(ont_country)[19:] + " Population: " + number)  # TODO DELETE


def build_country_area(country_doc, ont_country):
    index = int(country_doc.xpath(
        "count(//table[contains(@class,'infobox')][1]//tr[th//text()='Area ']/preceding-sibling::*)") + 2)
    if index == 2:
        index = int(country_doc.xpath(
            "count(//table[contains(@class,'infobox')]//tr[th//text()='Area']/preceding-sibling::*)") + 2)  # fixing, 'Area ' VS 'Area' issue
    area = str(country_doc.xpath("//table[contains(@class,'infobox')]//tr[" + str(index) + "]/td//text()")[0]).split()
    area = area[0] + "_km_squared"  # TODO see if it is better to add the km and squared only with the final answer
    ont_area = rdflib.URIRef(EXAMPLE + area)
    relation = rdflib.URIRef(EXAMPLE + "area_size")
    g.add((ont_country, relation, ont_area))


def build_country_form_of_government(country_doc, ont_country):
    GOVERNMENT_IN = rdflib.URIRef(EXAMPLE + "government_in")
    res = country_doc.xpath(
        "//table[contains(@class, 'infobox')]//tr[.//text()='Government']//td//@title")  # TODO make sure its the title what they asked for
    form_of_government = [government for government in res if government[0].isalpha()]
    for i in range(len(form_of_government)):
        g.add((rdflib.URIRef(EXAMPLE + form_of_government[i].replace(" ", "_")), GOVERNMENT_IN, ont_country))


def build_country(country_doc, ont_country):
    build_country_president(country_doc, ont_country)
    build_country_prime_minister(country_doc, ont_country)
    build_country_capital(country_doc, ont_country)
    build_country_area(country_doc, ont_country)
    build_country_form_of_government(country_doc, ont_country)
    build_country_population(country_doc, ont_country)


def get_country_from_question(question: str, substring: str, last_place: bool = True) -> str:
    # TODO check countries with 2 word name
    """
    return the country name from the question
    case 1 (default) - country is the last word in the question
    case 2 - country is the second last word in the question
    :rtype: str
    """
    idx = question.find(substring) + 1
    if (last_place):
        return question[idx + len(substring):len(question) - 1].replace(" ", "_")
    return question[idx + len(substring):len(question) - len(" born?")].replace(" ", "_")


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

    elif question.find("What is the population") != -1:
        country = get_country_from_question(question, "of")
        query = f"<{EXAMPLE + country}>  <{EXAMPLE}population_size> ?e."
        return "select * where {" + query + "}"

    elif question.find("Who is") != -1:
        name = question[7:len(question) - 1].replace(" ", "_")
        query = f"<{EXAMPLE + name}> <{EXAMPLE}is> ?e ."
        return "select * where {" + query + "}"

    elif question.find("How many") != -1:  # TODO count the answer
        # How many forms of government
        if question.find("are also") != -1:
            idx = question.find("are also")
            form1, form2 = question[9:idx - 1].replace(" ", "_"), question[idx + 9:len(question) - 1].replace(" ", "_")
            query = f"<{EXAMPLE + form1}> <{EXAMPLE}government_in> ?c ." + f" <{EXAMPLE + form2}> <{EXAMPLE}government_in> ?c ."
            return "select * where {" + query + "}"

        # How many presidents
        else:
            country = get_country_from_question(question, "in")
            query = f"?c <{EXAMPLE}place_of_birth> <{EXAMPLE + country}> ."
            return "select * where {" + query + "}"

    elif question.find("List all countries whose capital") != -1:
        substring = question.split()[-1].lower()  # returns the last word in the question - needs to be the substring
        query = f"?capital <{EXAMPLE}capital_of> ?country . filter (contains(LCASE(STR(?capital)), '{substring}') )"
        return "select ?country where {" + query + "} order by ?country"

    elif question.find("List all countries with") != -1: # new query - List all countries with population greater than {number}
        number = question.split()[-1]
        comma = '",", ""'
        #query =  f"<{EXAMPLE + country}> <{EXAMPLE}population_size> ?p ." + f" bind(REPLACE(STR(?p), {comma}) AS ?n)"
        query = f"?c <{EXAMPLE}population_size> ?p . filter(xsd:integer(REPLACE(STR(?p), {comma})) > xsd:integer({number}))"
        return "select ?c where {" + query + "} order by ?c"

def answer(query, question):  # TODO if the answer is None, return 0 instead
    query_result = g.query(query)
    need_to_count = "How many" in question
    if not need_to_count:
        return [ans[19:].replace("_", " ") for ans, *_ in query_result]

    else:
        for ans, *_ in query_result:
            return len(ans[19:].replace("_", " "))


# if sys.argv[1] == 'create':
#     build_countries_url()
#     for country in countries_url:
#         ont_country = country[1]
#         r = requests.get(country[0])
#         country_doc = lxml.html.fromstring(r.content)
#         build_country(country_doc, ont_country)
#         g.serialize("ontology.nt", format="nt")


# if sys.argv[1] == 'question': # TODO check this function
#     g.parse("ontology.nt", format="nt")
#     question = sys.argv[2]
#     query = build_query(question)
#     ans = answer(query, question)
#     print(*ans, sep=', ')


################## inputs #####################

# build_countries_url()
# count = 0 # TODO DELETE
# lst = ["China", "Portugal", "Guam", "Eswatini", "Tonga", "Argentina", "Sweden", "Bahrain"]
#  #"North Macedonia", "Iceland", "Fiji", "Lesotho", "Indonesia", "Uruguay", "Solomon Islands", "Lesotho", "Marshall Islands", "Republic of the Congo", "Republic of Ireland"]
# #        'Sierra_Leone', 'Ethiopia', 'Niue', 'Greenland', 'Andorra', 'Mongolia', 'Burundi', 'Guadeloupe', 'Rwanda', "Argentina", "Bhutan", "India", "Moldova",
# #        "Sint Maarten", "United States", "Mauritius", "Isle of Man", 'Tokelau', 'Djibouti', 'Mauritius', 'Luxembourg', "Saint Helena, Ascension and Tristan da Cunha"]
# # lst = [ "Eritrea"]
# for country in lst:
# # for country in countries_set:
#     country = country.replace(" ", "_")
#     r = requests.get("https://en.wikipedia.org/wiki/" + country)
#     doc = lxml.html.fromstring(r.content)
#     ont_country = rdflib.URIRef(EXAMPLE + country)
#     build_country(doc, ont_country)
#     count += 1 # TODO DELETE
#    # print(count)
# g.serialize("ontology.nt", format="nt")
# a = "List all countries with population greater than 50000000"
# b = build_query(a)
# g.parse("ontology.nt", format="nt")
# query_list_result = g.query(b)
# c = answer(query_list_result)
# print(*c, sep=', ')  # this is how we should print the results
# print(count) # TODO DELETE

build_countries_url()
for country in countries_url:
    ont_country = country[1]
    r = requests.get(country[0])
    country_doc = lxml.html.fromstring(r.content)
    build_country(country_doc, ont_country)

g.serialize("ontology.nt", format="nt")

a = "Who is David Kabua?"
b = build_query(a)
g.parse("ontology.nt", format="nt")
query_list_result = g.query(b)
c = answer(query_list_result)
print(*c, sep=', ')  # this is how we should print the results


# build_countries_url()
# for country in countries_url:
#     ont_country = country[1]
#     r = requests.get(country[0])
#     country_doc = lxml.html.fromstring(r.content)
#     build_country(country_doc, ont_country)
#
# g.serialize("ontology.nt", format="nt")


# TODO AVI: add order by to all queries which could have more than 1 answer - say to Tomer. - V
# TODO Avi: Saint_Helena,_Ascension_and_Tristan_da_Cunha name needs to dealt with. - V
# TODO Avi: ask Adam about COUNT is SPARQL queries
# TODO - make sure that in Republic of Ireland case, g should not include the place_of_birth relation (because the president place of birth is Ireland)
# TODO print answers right, not in an array or list - V
# TODO TOMER there are 3 countries that don't appear in the set, need to understand why. - found out that these are the last countries in the countries url
