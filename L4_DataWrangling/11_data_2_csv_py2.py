
# coding: utf-8

# ## References:
#     - https://github.com/pratyush19/Udacity-Data-Analyst-Nanodegree/tree/master/P3-OpenStreetMap-Wrangling-with-SQL
#     - Udacity course input
#     

# """
# Build CSV file from OSM. Parse, clean and shape data.
# """
# 
# """
# Rules:
# * We process only top level tags: **"node"**, **"way"**
# * We create two csv files of "node". One with empty child node called **nodes.csv** and other with "tag" child node called **nodes_tags.csv**
# * We create three csv files of "way". One with empty child node called **ways.csv**, other with "nd" child node called **ways_nodes.csv** and one with "tag" child node called **ways_tags.csv**
# * If the tag "k" value contains problematic characters, the tag should be ignored
# * If the tag "k" value contains a ":" the characters before the ":" should be set as the tag type
#   and characters after the ":" should be set as the tag key
# """

# In[2]:


import csv
import codecs
import re
import xml.etree.cElementTree as ET
from unittest import TestCase

import cerberus
import schema

OSM_PATH = "cuxhaven_sample_10.osm"
#OSM_PATH = "cuxhaven.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

streetmapping = { "Neukloster Str.": "Neukloster Straße",
            "KIefhorst": "Kiefhorst",
            "Kaemmererplatz": "Kämmererplatz"
            }

def update_name_german(name, streetmapping):
    better_name_german = name
    if name in streetmapping:
        better_name_german = streetmapping[name]
    return better_name_german


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    
    if element.tag == 'node':
        for key in element.attrib.keys():
            if key in node_attr_fields:
                node_attribs[key] = element.attrib[key]
        for child in element:
            if child.tag == 'tag':
                if problem_chars.search(child.attrib['k']):
                    pass
                else:
                    tags_list = {}
                    tags_list['id'] = element.attrib['id']
                    if child.attrib['k'] == 'addr:street':
                        tags_list['value'] = update_name_german(child.attrib['v'], streetmapping)
                    else:
                        tags_list['value'] = child.attrib['v']
                    if LOWER_COLON.search(child.attrib['k']):
                        colon_position = child.attrib['k'].find(':')
                        tags_list['key'] = child.attrib['k'][colon_position+1:]
                        tags_list['type'] = child.attrib['k'][:colon_position]
                    else:
                        tags_list['key'] = child.attrib['k']
                        tags_list['type'] = 'regular'
                    tags.append(tags_list)    
        
    if element.tag == 'way':
        for key in element.attrib.keys():
            if key in way_attr_fields:
                way_attribs[key] = element.attrib[key]
        position = 0
        for child in element:
            
            if child.tag == 'nd':
                way_nodes_list = {}
                way_nodes_list['id'] = element.attrib['id']
                way_nodes_list['node_id'] = child.attrib['ref']
                way_nodes_list['position'] = position
                position += 1
                way_nodes.append(way_nodes_list)
            if child.tag == 'tag':
                if problem_chars.search(child.attrib['k']):
                    pass
                else:
                    tags_list = {}
                    tags_list['id'] = element.attrib['id']
                    if child.attrib['k'] == 'addr:street':
                        tags_list['value'] = update_name_german(child.attrib['v'], streetmapping)
                    else:
                        tags_list['value'] = child.attrib['v']
                    if LOWER_COLON.search(child.attrib['k']):
                        colon_position = child.attrib['k'].find(':')
                        tags_list['key'] = child.attrib['k'][colon_position+1:]
                        tags_list['type'] = child.attrib['k'][:colon_position]
                    else:
                        tags_list['key'] = child.attrib['k']
                        tags_list['type'] = 'regular'
                    tags.append(tags_list)  
            
    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_strings = (
            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
            for k, v in errors.iteritems()
        )
        raise cerberus.ValidationError(
            message_string.format(field, "\n".join(error_strings))
        )


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    process_map(OSM_PATH, validate=False)

