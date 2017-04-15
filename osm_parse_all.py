# -*- coding: utf-8 -*-
"""
Class for auditing data for settlements in OSM files
within Texas, USA.
"""

import csv
import os
import pandas as pd
import sqlite3
import time
import xml.etree.cElementTree as ET

class Popul(object):
    
    def __init__(self, file_name=None, url=None):
        self.file_name = file_name
        self.pop_est = {}
        self.node_data = []
        self.tag_data = []
    
    def get_element(self, tags=('node', 'way', 'relation')):
        # Element iterator for parsing and counting nodes, borrowed from lessons
        context = ET.iterparse(self.file_name, events=('start', 'end'))
        __, root = next(context)
        for event, elem in context:
            if event == 'end' and elem.tag in tags:
                yield elem
                root.clear()

    def reset_data_files(self):
        # Deletes and re-initializes csv files
        for each in ['node_attribs.csv', 'way_attribs.csv', 'relation_attribs.csv', 'p3_osm5']:
            try:
                os.remove(each)
            except:
                continue
        

                
    def process_data(self):
        count = 0
        count2 = 0
        time_start = time.time()
        print("Processing OSM file...")
        # Reset data files to avoid data duplication
        self.reset_data_files()
        initialized = []
        for element in self.get_element():
            count += 1 
            attribs_df = pd.DataFrame(element.attrib, index=[0,])
            if '{}_attribs.csv'.format(element.tag) in initialized:
                attribs_df.to_csv('{}_attribs.csv'.format(element.tag), mode='a', header=False)
            else:
                attribs_df.to_csv('{}_attribs.csv'.format(element.tag))
                initialized.append('{}_attribs.csv'.format(element.tag))
            if len(element) == 0:
                continue
            for child in element:
                if child.tag == 'tag':
                    child_df = pd.DataFrame(child.attrib, index=[0])
                    if 'tag_attribs.csv' in initialized:
                        child_df.to_csv('tag_attribs.csv', mode='a', header=False)
                    else:
                        child_df.to_csv('tag_attribs.csv')
                        initialized.append('tag_attribs.csv')
        
        time_end = time.time()
        total_time = round(time_end - time_start, 4)
        print("Data processed in {} secs. \n{} elements and {} tags found and cleaned.".format(total_time, count, count2))

    

        

    def write_sql(self):
        # Writes csv data to sql files
        nodes_df = pd.read_csv(self.node_file_name)
        places_df = pd.read_csv(self.place_file_name)
        popul_df = pd.read_csv(self.popul_file_name)
        connect = sqlite3.connect(r'p3_osm5')
        cur = connect.cursor()
        cur.execute('DROP TABLE IF EXISTS settlement_nodes;')
        cur.execute('DROP TABLE IF EXISTS settlement_places;')
        cur.execute('DROP TABLE IF EXISTS settlement_popul;')
        nodes_df.to_sql('settlement_nodes', connect)
        places_df.to_sql('settlement_places', connect)
        popul_df.to_sql('settlement_popul', connect)
        connect.commit()
        connect.close()



        
if __name__ == '__main__':        

    # Initialize Austin OSM data object
    a = Popul(r'houston_texas.osm')
    
    # Initialize dictionary of TDC population estimates
#    a.get_popul_est()
    
    # Parse and clean xml file, write data to csv files
    a.process_data()
#    
#    # Write data to SQL database
#    a.write_sql()
#    
#    # Query SQL database for descriptive stats of population data and data changes
#    a.get_pop_edits()
#    a.get_pop_change_list()
#    a.get_averages()
#    a.get_designation_changes()
#    a.get_sources()
#    a.get_users()
