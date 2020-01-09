# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 13:47:21 2020

@author: simon
"""

import requests					# requesting webpages
from bs4 import BeautifulSoup 	# parsing html
import json
import optparse

parser = optparse.OptionParser('get-lszs')
parser.add_option('-o', '--outdir',	dest='outdir', help='[optional] output directory')
parser.add_option('-s', '--single-file',	action='store_true', dest='single', help='[optional] output directory')
(opts, args) = parser.parse_args()

headers = { 'Host' : 'www.bernairport.ch',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:2.0) Gecko/20100101 Firefox/72.0',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language' : 'en-US,en;q=0.5',
            'Accept-Encoding' : 'utf-8',
            'DNT' : '1',
            'Connection' : 'keep-alive',
            'Upgrade-Insecure-Requests' : '1',
            'Cookie-Installing-Permission' : 'required',
            'Cache-Control' : 'max-age=0',
            'TE' : 'Trailers' }

def getLSZB(tabletyp):
    requrl = 'https://www.bernairport.ch/en/'
    # website currently does not require to send the headers
    response = requests.get(requrl)
    
    if(response.status_code != 200):
        print('error: Website returned status code: ' + str(response.status_code))
    
    keyword = 'arrivaltable'
    if('dep' in tabletyp.lower()):
        keyword = 'departuretable'
    parsed_html = BeautifulSoup(response.text, 'lxml')
    flt_table = parsed_html.find('table', {'class': keyword}).find('tbody')
    rows = flt_table.findAll('tr')
    
    # prepare json dict with empty array
    timetable = {}
    timetable['data'] = []
    
    for row in rows:
        entry = {}
        if(row.find('th') is None):   # ignore table header
            entry['flightNo']      = row.find('td', {'class', 'flightNo'}).text
            entry['airport']       = row.find('td', {'class', 'airport'}).text
            entry['via']           = row.find('td', {'class', 'via'}).text
            entry['scheduledTime'] = row.find('td', {'class', 'scheduledTime'}).text
            entry['estimatedTime'] = row.find('td', {'class', 'estimatedTime'}).text
            if('dep' in tabletyp.lower()):
                entry['gate']          = row.find('td', {'class', 'gate'}).text  # gate only with departures
            entry['status']        = row.find('td', {'class', 'status'}).text
            entry['privateflight'] = row.find('td', {'class', 'privateflight'}).text
            entry['direction'] = 'departure' if 'dep' in tabletyp.lower() else 'arrival'
            timetable.append(entry)
    
            timetable['data'].append(entry)
    return timetable

def writeJsonFile(filename, data):
    with open(str(filename), 'w') as outfile:
        json.dump(data, outfile)
        
def getTime(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return int(json['page']['update_time'])
    except KeyError:
        return 0

#%%
def main():
    try:
        outdir = '.'
        if(opts.outdir is not None):
            outdir = opts.outdir
            
        if(opts.single is not None):
            table = getLSZB('arr')
            table = table + getLSZB('dep')
            # sort by arrital time
            table = sorted(table, key=lambda k: k['scheduledTime']) 
            writeJsonFile(outdir + '/timetable.json', table)
        else:
            table = getLSZB('arr')
            writeJsonFile(outdir + '/arrivals.timetable.json', table)
            table = getLSZB('dep')
            writeJsonFile(outdir + '/departures.timetable.json', table)
        
    except KeyboardInterrupt:
        print('')
        exit(0)


if __name__ == '__main__':
	main()
    
    
