# -*- coding: utf-8 -*-
"""
Class for auditing and cleaning population data for settlements in OSM files
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

    def initialize_csvs(self):
        # Initialize csv files for later writing and export into SQL
        self.node_file_name = 'node_attribs.csv'
        self.node_csv = open(self.node_file_name, 'w')
        self.write_node_csv = csv.writer(self.node_csv)
        
        self.place_file_name = 'place_data.csv'
        self.place_csv = open(self.place_file_name, 'w')
        self.write_place_csv = csv.writer(self.place_csv)
        
        self.popul_file_name = 'popul_data.csv'
        self.popul_csv = open(self.popul_file_name, 'w')
        self.write_popul_csv = csv.writer(self.popul_csv)
        
        self.write_node_csv.writerow(('node_id', 'user', 'uid', 'timestamp'))
        self.write_place_csv.writerow(('node_id', 'name', 'place', 'place_change'))
        self.write_popul_csv.writerow(('name', 'osm_population', 'pop_2016', 'source'))
        
        self.node_csv.close()
        self.place_csv.close()
        self.popul_csv.close()

    
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
        for each in ['node_attribs.csv', 'place_data.csv', 'popul_data.csv', 'p3_osm5']:
            try:
                os.remove(each)
            except:
                continue
        
        self.initialize_csvs()
            
    def write_node_data(self, data):
        # Write function for appending new data to existing csv file
        # 'node_attribs.csv'
        assert len(data) == 4
        node_csv = open('node_attribs.csv', 'a')
        writer = csv.writer(node_csv)
        writer.writerow(data)
        node_csv.close()
        
    def write_place_data(self, data):
        # Write function for appending new data to existing csv file
        # 'place_data.csv'
        assert len(data) == 4
        place_csv = open('place_data.csv', 'a')
        writer = csv.writer(place_csv)
        writer.writerow(data)
        place_csv.close()
    
    def write_popul_data(self, data):
        # Write function for appending new data to existing csv file
        # 'popul_data.csv'
        assert len(data) == 4
        popul_csv = open('popul_data.csv', 'a')
        writer = csv.writer(popul_csv)
        writer.writerow(data)
        popul_csv.close()
    
        
    def get_popul_est(self, f=r"2015_txpopest_place.csv"):
        # Read csv file of Texas gov population estimates into city keyed dict
        reader = csv.reader(open(f))
        for row in reader:
            #row[2] = 2010 US Census figure, row[4] = Texas estimate for 1-1-2016
            self.pop_est[row[1]] = [row[2], row[4]] 
            
    def shape_source_helper(self):
        # Checks and updates OSM population data source
        if self.tag_data[5] == 'US Census':
            # Assumes US Census synonymous with US Census 2010
            self.tag_data[5] == 'US Census 2010'
        if self.tag_data[5] == None and self.tag_data[3] == self.pop_est[self.tag_data[0]][0]:
            # Assumes original source was 2010 census if pop values equal
            self.tag_data[5] = 'US Census 2010'
            
                
    def shape_data(self):
        # Update population figures to most recent gov estimates
        # Update OSM settlement type based on revised population figures
        # Input: list of len = 7, 
        #        [OSM node id, city name, OSM settlement type, T/F for settlement type change,
        #         OSM population, revised population (init None), OSM pop source]
        # Output: None
        osm_pop = int(self.tag_data[3])
        name = self.tag_data[0]
        pop_2016 = int(self.pop_est[name][1])
        if pop_2016 != osm_pop:
            self.tag_data[4] = int(pop_2016)
            place = None
            if pop_2016 < 100:
                place = 'hamlet'
            elif pop_2016 <10000:
                place = 'village'
            elif pop_2016 <100000:
                place = 'town'
            else:
                place = 'city'
                
            if place != self.tag_data[1]:
                self.tag_data[1] = place
                self.tag_data[2] = True
        else:
            self.tag_data[4] = osm_pop
        self.shape_source_helper()

        
    def process_data(self):
        # Parse, audit and update OSM population data
        # Extracted and cleaned data written to csv files
        count = 0
        time_start = time.time()
        print("Processing OSM file...")
        # Reset data files to avoid data duplication
        self.reset_data_files()
        settlements = set([])
        for element in self.get_element():
            self.tag_data = []
            # Gather element data for later OSM correction
            elem_id = element.get('id')
            time_stamp_year = element.get('timestamp')[:4]
            user = element.get('user')
            user_id = element.get('uid')
            self.node_data = [elem_id, user, user_id, time_stamp_year]
            # Define and reset tag variables
            name = None
            place = None
            popul = None
            source = None
            # Gather tag data
            for tag in element.iter('tag'):
                if tag.attrib['k'] == 'name':
                    name = tag.get('v')
                if tag.attrib['k'] == 'place':
                    place = tag.get('v')
                if tag.attrib['k'] == 'population':
                    popul = tag.get('v') 
                if tag.attrib['k'].startswith('source:population'):
                    source = tag.get('v')
            # Write element and tag data to respective csv files
            if (name in self.pop_est and name not in settlements and popul):
                settlements.add(name)
                count += 1
                self.tag_data = [name, place, False, popul, None, source] 
                self.shape_data()
                self.tag_data = [elem_id] + self.tag_data
                self.write_node_data(self.node_data)
                self.write_place_data(self.tag_data[:4])
                self.write_popul_data([name] + self.tag_data[4:])
        time_end = time.time()
        total_time = round(time_end - time_start, 4)
        print("Data processed in {} secs. \n{} population tags found and cleaned.".format(total_time, count))

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

    def get_pop_edits(self):
        p3_db = sqlite3.connect(r'p3_osm5')
        curs = p3_db.cursor()
        curs.execute("SELECT COUNT(name) FROM settlement_places;")
        n = curs.fetchone()[0]
        print("Number of revised populations = {}".format(n))
        print()
        curs.close()
    
    def get_pop_change_list(self):
        p3_db = sqlite3.connect(r'p3_osm5')
        curs = p3_db.cursor()
        curs.execute("SELECT name, pop_2016 - osm_population,\
                             round(((pop_2016 - osm_population)/(osm_population*1.0)), 3) AS proportion\
                             FROM settlement_popul \
                             ORDER BY proportion;")
        settlements = curs.fetchall()
        # Convert back to Pandas df to print cleanly
        settlements_df = pd.DataFrame(settlements, columns=('Settlement', 'Increase', 'Proportion'))
        print(settlements_df)
        print()
        curs.close()
        
    def get_averages(self):
        p3_db = sqlite3.connect(r'p3_osm5')
        curs = p3_db.cursor()
        curs.execute("SELECT round(avg(pop_2016 - osm_population), 2) AS average_increase,\
                             avg(1.0 * round(((pop_2016 - osm_population)/(1.0 * osm_population)), 4)) AS proportion\
                             FROM settlement_popul;")
        incr_avg, prop_avg = curs.fetchone()
        print("Mean population increase = {}  \nMean proportional increase = {}".format(incr_avg, prop_avg))
        print()
        curs.close()
        
    def get_designation_changes(self):
        p3_db = sqlite3.connect(r'p3_osm5')
        curs = p3_db.cursor()
        curs.execute("SELECT sum(place_change) AS Place_Changes FROM settlement_places;")
        n_place_change = curs.fetchone()[0]
        
        print("Number of place designations changed = {}".format(n_place_change))
        print()
        curs.execute("SELECT name, place FROM settlement_places WHERE place_change == 1")
        place_change = curs.fetchall()
        # Convert back to Pandas df to print cleanly
        place_change_df = pd.DataFrame(place_change, columns=('Settlement', 'New Designation'))
        print(place_change_df)
        print()
        curs.close()
        
    def get_sources(self):
        p3_db = sqlite3.connect(r'p3_osm5')
        curs = p3_db.cursor()
        curs.execute("SELECT source, COUNT(*) AS Count FROM settlement_popul GROUP BY source ORDER BY Count DESC;")
        source_count = curs.fetchall()
        source_df = pd.DataFrame(source_count, columns=('Data Source', 'Count'))
        print(source_df)
        print()
        curs.close()
        
    def get_users(self):
        p3_db = sqlite3.connect(r'p3_osm5')
        curs = p3_db.cursor()
        curs.execute("SELECT user, COUNT(uid) AS Count FROM settlement_nodes GROUP BY user ORDER BY Count DESC;")
        source_count = curs.fetchall()
        source_df = pd.DataFrame(source_count, columns=('Contributors', 'Contribution Count'))
        print(source_df)
        print()
        curs.close()

    def get_timestamp(self):
        p3_db = sqlite3.connect(r'p3_osm5')
        curs = p3_db.cursor()
        curs.execute("SELECT timestamp, COUNT(timestamp) FROM settlement_nodes ORDER BY Count DESC;")
        timestamp = curs.fetchall()
        timestamp_df = pd.DataFrame([timestamp], columns=('Year of Data', 'Count'))
        print(timestamp_df)
        print()
        curs.close()

