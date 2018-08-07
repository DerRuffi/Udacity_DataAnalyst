
# coding: utf-8

# Your task is to explore the data a bit more.
# Before you process the data and add it into your database, you should check the
# "k" value for each "<tag>" and see if there are any potential problems.
# 
# We have provided you with 3 regular expressions to check for certain patterns
# in the tags. As we saw in the quiz earlier, we would like to change the data
# model and expand the "addr:street" type of keys to a dictionary like this:
# {"address": {"street": "Some value"}}
# So, we have to see if we have such tags, and if we have any tags with
# problematic characters.
# 
# Please complete the function 'key_type', such that we have a count of each of
# four tag categories in a dictionary:
#   "lower", for tags that contain only lowercase letters and are valid,
#   "lower_colon", for otherwise valid tags with a colon in their names,
#   "problemchars", for tags with problematic characters, and
#   "other", for other tags that do not fall into the other three categories.
# See the 'process_map' and 'test' functions for examples of the expected format.

# In[1]:


import xml.etree.cElementTree as ET
import pprint
import re

from collections import defaultdict


# In[2]:


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

OSMFILE = "cuxhaven.osm"


# In[3]:


def key_type(element, keys):
    if element.tag == "tag":
        for tag in element.iter('tag'):
            k = tag.get('k')
            if lower.search(element.attrib['k']):
                keys['lower'] = keys['lower'] + 1
            elif lower_colon.search(element.attrib['k']):
                keys['lower_colon'] = keys['lower_colon'] + 1
            elif problemchars.search(element.attrib['k']):
                keys['problemchars'] = keys['problemchars'] + 1
            else:
                keys['other'] = keys['other'] + 1
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys


# In[ ]:


dict1 = process_map(OSMFILE)
pprint.pprint(dict1)


# In[ ]:


lower_tags = []
lowercol_tags = []
prob_tags = []
other_tags = []
def key_type(element, keys):
    if element.tag == "tag":
        for tag in element.iter('tag'):
            k = tag.get('k')
            if lower.search(element.attrib['k']):
                keys['lower'] = keys['lower'] + 1
                lower_tags.append(element.attrib['k'])
            elif lower_colon.search(element.attrib['k']):
                keys['lower_colon'] = keys['lower_colon'] + 1
                lowercol_tags.append(element.attrib['k'])
            elif problemchars.search(element.attrib['k']):
                keys['problemchars'] = keys['problemchars'] + 1
                prob_tags.append(element.attrib['k'])
            else:
                keys['other'] = keys['other'] + 1
                other_tags.append(element.attrib['k'])
    
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys


# In[24]:


dict1 = process_map(OSMFILE)
sorted(set(other_tags)) #by convering to a set, we can remove dublicates

