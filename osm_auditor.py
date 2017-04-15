# -*- coding: utf-8 -*-
"""
OpenStreetMap Auditor
"""

import os
import time
import xml.etree.cElementTree as ET


class Audit(object):
    
    def __init__(self, file_name):
        self.file_name = file_name

    def get_element(self, tags=('node', 'way', 'relation')):
        # Element iterator for parsing and counting nodes, borrowed from lessons
        context = ET.iterparse(self.file_name, events=('start', 'end'))
        __, root = next(context)
        for event, elem in context:
            if event == 'end' and elem.tag in tags:
                yield elem
                root.clear()
    
    def get_elem_attribs(self):
        attribs = {'node': set([]), 'way': set([]), 'relation': set([])}
        
        for element in self.get_element():
            for a in element.attrib:
                attribs[element.tag].add(a)
        print(attribs)
        
    def get_file_size(self):
        # Print opened file size
        size = os.stat(self.file_name).st_size        
        print("\nOpened OSM file size = {} megabytes".format(round(size/float(1000000), 2)))
    
    def get_osm_stats(self):
        # Prints counts for element tags in set(node, way, relation)
        print("\nCounting element tags in file...")
        counts = {'node':0, 'way':0, 'relation':0}
        
        for element in self.get_element():
            counts[element.tag] += 1
        
        for key in counts:
            print("{}s in {} = {}".format(key.capitalize(), self.file_name, counts[key]))
    
    def get_tag_names(self):
        tag_names = set([])
        for element in self.get_element():
            if len(element) > 0:
                for child in element:
                    tag_names.add((child.get('k'), child.get('v')))
        return tag_names
            
    def audit_streets(self):
        # Compile set of unique street types using split, take last element approach
        time_start = time.time()
        tag_values = set([])
        print("\nProcessing OSM file...")
        for element in self.get_element():
            for tag in element.iter('tag'):
                if tag.attrib['k'] == 'addr:street':
                    name = tag.get('v').split(" ")[-1]
                    tag_values.add(name)
        time_end = time.time()
        total_time = round(time_end - time_start, 4)
        print("Data processed in {} secs. \n\nResulting set of tag values for street type: \n".format(total_time))
        print(tag_values)     
            
    def audit_tags(self, tag_name):
        # Compile set of unique values for given tage name.
        time_start = time.time()
        tag_values = set([])
        print("\nProcessing OSM file...")
        for element in self.get_element():
            for tag in element.iter('tag'):
                if tag.attrib['k'] == tag_name:
                    name = tag.get('v')
                    tag_values.add(name)


        time_end = time.time()
        total_time = round(time_end - time_start, 4)
        print("Data processed in {} secs. \n\nResulting set of values for tag_name = {}: \n".format(total_time, tag_name))
        print(tag_values)

if __name__ == '__main__':
        
    # Initialize Austin OSM audit object
    a = Audit(r'houston_texas.osm')
    
    # Audit file
    a.get_elem_attribs()
#    a.get_file_size()
#    a.get_osm_stats()
#    a.audit_streets()
#    a.audit_tags('addr:postcode')