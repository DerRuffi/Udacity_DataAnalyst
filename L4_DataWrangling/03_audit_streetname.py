
# coding: utf-8

# In[1]:


import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint


# - audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
#     the unexpected street types to the appropriate ones in the expected list.
#     You have to add mappings only for the actual problems you find in this OSMFILE,
#     not a generalized solution, since that may and will depend on the particular area you are auditing.
# - write the update_name function, to actually fix the street name.
#     The function takes a string with street name as an argument and should return the fixed name
#    

# In[16]:


OSMFILE = "cuxhaven.osm"
#OSMFILE = "cuxhaven_sample_50.osm"
#street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_type_re = re.compile(r'.*', re.IGNORECASE)

#expected = ["Straße", "Weg", "Stieg", "Gang", "Ring", "Chaussee"]

# UPDATE THIS VARIABLE
streetmapping = { "Neukloster Str.": "Neukloster Straße",
            "KIefhorst": "Kiefhorst",
            "Rd.": "Road"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        #if street_type not in expected:
        street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r", encoding="utf8")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

#pprint.pprint(dict(audit(OSMFILE))) # print the existing names

def update_name(name, streetmapping):
    m = street_type_re.search(name)
    better_name = name
    if m:
        better_street_type = streetmapping[m.group()]
        better_name = street_type_re.sub(better_street_type, name)
    return better_name

def update_name_german(name, streetmapping):
    better_name_german = name
    if name in streetmapping:
        better_name_german = streetmapping[name]
    return better_name_german


# In[17]:


#pprint.pprint(dict(audit(OSMFILE))) # print the existing names


# Street names in german are set together in a quite complicated way. The oficial rules are listed in this reference:
# 
# https://www.duden.de/sprachwissen/rechtschreibregeln/strassennamen
# 
# In  nutshell, you can expect all kind of settings, like:
# "Hauptstraße" (general case)
# "Leipziger Straße" (Leipzig is a city, causing an expection to seperate "Straße") 
# "Georg-Büchner-Straße" (Georg Büchner is a person, causing an expection to use "-")
# 
# To automatize a correction function to check for the applicable rule for a certain street name is very ambicious and would cetainly exceed the time related to this project.
# 
# Anyhow, we can check for more obvious mistakes, like abbreviations.
# Abbreviations are in general not allowed in German Streetnames, of course with a few exceptions.
# The openstreetmap abbreviation list can be found here:
# 
# https://wiki.openstreetmap.org/wiki/Name_finder:Abbreviations#Deutsch_-_German
# 
# One can see that abbreviations are either followed by a "." (excepection Bhf = Bahnhof = railway station) or written in capital latters. Multiple grouped capital letters are in german only used for this purpose to my knowledge.

# In[5]:


#Search for streetnames including "."
street_type_re = re.compile(r'\.', re.IGNORECASE)
pprint.pprint(dict(audit(OSMFILE))) # print the existing names
#the abbreviation "St." stands for "Sankt" and is correctly used within this list.


# In[6]:


#Search for streetnames including "." after word boundary and multiple non-whitespaces
street_type_re = re.compile(r'\b\S+\.$', re.IGNORECASE)
pprint.pprint(dict(audit(OSMFILE))) # print the existing names


# In[7]:


#Search for railway station abbreviation
street_type_re = re.compile(r'Bhf')
pprint.pprint(dict(audit(OSMFILE))) # print the existing names


# As written above, 2 or more capital letters in a row a very unusual in german and might be caused by a mistype.

# In[8]:


street_type_re = re.compile(r'[A-Z]{2}')
pprint.pprint(dict(audit(OSMFILE))) # print the existing names


# The romatic numbers are likely to be correct part of the street names. So we need to be more precise in checking for mistypes, adding at least 1 additional lower case letter:

# In[9]:


street_type_re = re.compile(r'[A-Z]{2}[a-z]{1}')
pprint.pprint(dict(audit(OSMFILE))) # print the existing names


# In[10]:


#Let's check for the mutated vowel "ae", which is correctly written "ä"
street_type_re = re.compile(r'ae')
pprint.pprint(dict(audit(OSMFILE))) # print the existing names
#all printed names are correct


# In[11]:


#update_street = audit(OSMFILE) 
# print the updated names
#for street_type, ways in update_street.items():
#    for name in ways:
#        better_name = update_name(name, streetmapping)
#print (name, "=>", better_name)


# In[15]:


print (update_name_german("Neukloster Str.",streetmapping))

