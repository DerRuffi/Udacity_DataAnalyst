
# coding: utf-8

# In[9]:


import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint


# In[11]:


OSMFILE = "cuxhaven.osm"
#street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_type_re = re.compile(r'.*', re.IGNORECASE)

# UPDATE THIS VARIABLE
streetmapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road"
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_types[street_type].add(street_name)


def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit(osmfile):
    osm_file = open(osmfile, "r", encoding="utf8")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
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


# In[12]:


postcode1 = dict(audit(OSMFILE))
#pprint.pprint(postcode1) # print the existing names
print(len(postcode1))


# In[13]:


#Search for post codes not matching the 5-digits format:
street_type_re = re.compile(r'[^\d]{5}', re.IGNORECASE)
pprint.pprint(dict(audit(OSMFILE))) # print the existing names


# In[19]:


#update_street = audit(OSMFILE) 
# print the updated names
#for street_type, ways in update_street.items():
#    for name in ways:
#        better_name = update_name(name, streetmapping)
#print (name, "=>", better_name)

