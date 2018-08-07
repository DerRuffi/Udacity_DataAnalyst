
# coding: utf-8

# In[5]:


import xml.etree.cElementTree as ET
import pprint


OSMFILE = "cuxhaven_sample_50.osm"


# In[6]:


#count the numbers of unique tag
def count_tags(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag in tags: 
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    return tags
    
pprint.pprint(count_tags(OSMFILE))

