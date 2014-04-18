#! /usr/bin/python

## Copyright 2014 Kalanand Mishra

## myLinksAnalyzer is a free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License or any later version: <http://www.gnu.org/licenses/>.
## This software is distributed WITHOUT ANY WARRANTY. 

## Instructions: The executable is 'analyze.py'. You can 
## modify it according to your needs.
## You can either run a brand-new query (which is the default) or 
## analyze data stored in a text file from a previous query. 

##  _   _                                                          
## | \ | | _____      __   __ _ _   _  ___ _ __ _   _    ___  _ __ 
## |  \| |/ _ \ \ /\ / /  / _` | | | |/ _ \ '__| | | |  / _ \| '__|
## | |\  |  __/\ V  V /  | (_| | |_| |  __/ |  | |_| | | (_) | |   
## |_| \_|\___| \_/\_/    \__, |\__,_|\___|_|   \__, |  \___/|_|   
##                           |_|                |___/              
##                     _    __                        __ _ _      
##  _ __ ___  __ _  __| |  / _|_ __ ___  _ __ ___    / _(_) | ___ 
## | '__/ _ \/ _` |/ _` | | |_| '__/ _ \| '_ ` _ \  | |_| | |/ _ \
## | | |  __/ (_| | (_| | |  _| | | (_) | | | | | | |  _| | |  __/
## |_|  \___|\__,_|\__,_| |_| |_|  \___/|_| |_| |_| |_| |_|_|\___|
##                                                                

readStoredData = False


##  _                            _   
## (_)_ __ ___  _ __   ___  _ __| |_ 
## | | '_ ` _ \| '_ \ / _ \| '__| __|
## | | | | | | | |_) | (_) | |  | |_ 
## |_|_| |_| |_| .__/ \___/|_|   \__|
##             |_|                   

import sys, os, getopt, re, urllib
import json, csv
from linkedin import linkedin # pip install python-linkedin
from prettytable import PrettyTable # pip install prettytable
import numpy as np



#########################################################################
##   ___                          _   _               _    ____ ___    ##
##  / _ \ _   _  ___ _ __ _   _  | |_| |__   ___     / \  |  _ \_ _|   ##
## | | | | | | |/ _ \ '__| | | | | __| '_ \ / _ \   / _ \ | |_) | |    ##
## | |_| | |_| |  __/ |  | |_| | | |_| | | |  __/  / ___ \|  __/| |    ##
##  \__\_\\__,_|\___|_|   \__, |  \__|_| |_|\___| /_/   \_\_|  |___|   ##
##                        |___/                                        ##
############ Parameters needed to query the LinkedIn API ###############
## From: https://www.linkedin.com/secure/developer.
## Get CONSUMER_KEY, CONSUMER_SECRET, USER_TOKEN, and USER_SECRET credentials 

API_KEY = ''  
API_SECRET = ''  
USER_TOKEN = ''
USER_SECRET = ''

RETURN_URL = 'http://localhost:8000' # Not required for developer authentication

connections_data = 'linkedin_connections.json'
profile_data = 'linkedin_myprofile.json'


##  __  __       _       
## |  \/  | __ _(_)_ __  
## | |\/| |/ _` | | '_ \ 
## | |  | | (_| | | | | |
## |_|  |_|\__,_|_|_| |_|
##                       
################ The main function ########################

if __name__ == "__main__":

    if readStoredData : 
        myprofile = json.loads(open(profile_data).read())
        connections = json.loads(open(connections_data).read())
        print "Your profile:" 
        print myprofile
        print "Your connections:"
        print connections
    else :
        # Instantiate the developer authentication class    
        auth = linkedin.LinkedInDeveloperAuthentication(API_KEY, API_SECRET, 
                                                        USER_TOKEN, USER_SECRET, 
                                                        RETURN_URL, 
                                                        permissions=linkedin.PERMISSIONS.enums.values())
        
        # Pass it in to the app...
        app = linkedin.LinkedInApplication(auth)
        
        # Print my profile
        myprofile = app.get_profile()
        print "Your profile:"
        print myprofile
        
        # Write my profile to a file
        f = open(profile_data, 'w')
        f.write(json.dumps(myprofile, indent=1))
        f.close()


        # Print all my connections
        connections = app.get_connections()
        print "Your connections:"
        print connections

        # Write my connections to a file
        f = open(connections_data, 'w')
        f.write(json.dumps(connections, indent=1))
        f.close()

    ###################################################
    ## Pretty-printing your LinkedIn connections' data
    ###################################################
    pt = PrettyTable(field_names=['Name', 'Location', 'Industry', 'Country'])
    pt.align = 'l'
    
    [ pt.add_row((c['firstName'] + ' ' + c['lastName'], c['location']['name'], 
                  c['industry'], c['location']['country']['code'])) 
      for c in connections['values']
      if c.has_key('location') and c.has_key('industry')]

    print pt

    ##############################################################################
    from geopy import geocoders 
    #from geopy.geocoders import GoogleV3
    #geolocator = geocoders.GoogleV3()
    GEO_APP_KEY = '' # XXX: Get this from https://www.bingmapsportal.com
    g = geocoders.Bing(GEO_APP_KEY)
    # address, (latitude, longitude) = geolocator.geocode("Chicago", exactly_one=False)
    # print(address, latitude, longitude)
    #print g.geocode("Chicago", exactly_one=False)
    
    transforms = [('Greater ', ''), (' Area', '')]
    results = {}

    ######## Location ##########
    nCountries = {}
    nCountries['US'] = 0
    nCountries['EU'] = 0
    nCountries['CERN'] = 0 
    nCountries['India'] = 0
    nCountries['Other'] = 0

    nCities = {}
    nCities['Geneva'] = 0
    nCities['Chicago'] = 0
    nCities['SF Bay'] = 0

    ######## Profession ##########
    nProf = {}
    nProf['Research'] = 0
    nProf['Education'] = 0
    nProf['Finance']  = 0 
    nProf['Data science']  = 0 
    nProf['Engineering']  = 0 
    nProf['Biotech']  = 0 
    nProf['Other']  = 0 
    nProf['Unknown'] = 0

    ######## Headline words ##########
    nHline = {}
    nHline['Fermilab'] = 0
    nHline['Physics'] = 0
    nHline['Scientist'] = 0
    nHline['Data'] = 0
    nHline['Professor'] = 0
    nHline['Research'] = 0
    nHline['Postdoc'] = 0
    nHline['Engineer'] = 0
    nHline['University'] = 0
    nHline['Associate'] = 0

    ##  _                                            
    ##  | |    ___   ___  _ __     _____   _____ _ __ 
    ##  | |   / _ \ / _ \| '_ \   / _ \ \ / / _ \ '__|
    ##  | |__| (_) | (_) | |_) | | (_) \ V /  __/ |   
    ##  |_____\___/ \___/| .__/   \___/ \_/ \___|_|   
    ##                   |_|                          
    ##                                   _   _                 
    ##    ___ ___  _ __  _ __   ___  ___| |_(_) ___  _ __  ___ 
    ##   / __/ _ \| '_ \| '_ \ / _ \/ __| __| |/ _ \| '_ \/ __|
    ##  | (_| (_) | | | | | | |  __/ (__| |_| | (_) | | | \__ \
    ##   \___\___/|_| |_|_| |_|\___|\___|\__|_|\___/|_| |_|___/
    ##                                                         

    for c in connections['values']:

        # Let's check their headline
        if c.has_key('headline') :
            for k in nHline.keys():
                if k in c['headline']: nHline[k] += 1

        # Let's check their profession
        if c.has_key('industry'): 
            if 'Research' in c['industry']: nProf['Research'] += 1
            elif ('Education' in c['industry'] or 'Learning' in 
                  c['industry']): nProf['Education'] += 1
            elif ('Information' in c['industry'] or 
                  'Internet' in c['industry'] or 'Software' 
                  in c['industry']): nProf['Data science'] +=1
            elif ('Financial' in c['industry'] or 
                  'Recruiting' in c['industry'] or 'Banking' 
                  in c['industry'] or 'Retail' in c['industry'] or 
                  'Investment' in c['industry'] or "Quant" in 
                  c['industry']): nProf['Finance'] +=1
            elif ('Semiconductors' in c['industry'] or 
                  'Design' in c['industry']): nProf['Engineering'] +=1
            elif ('Pharmaceuticals' in c['industry'] or 
                  'Hospital' in c['industry'] or 'Health' 
                  in c['industry'] or 'Biotechnology' 
                  in c['industry']): nProf['Biotech'] += 1
            else: nProf['Other'] += 1   #Govt, Renewables, Environment, law,...
        else: nProf['Unknown'] += 1


        # Let's check their location
        if not c.has_key('location') : continue 
        if (c['location']['country']['code'] == u'us' 
            or c['location']['country']['code'] == u'ca'): 
            nCountries['US'] += 1
        elif c['location']['country']['code'] == u'in' : 
            nCountries['India'] += 1
        elif c['location']['country']['code'] == u'ch' : 
            nCountries['CERN'] += 1
            nCities['Geneva'] += 1 
        elif (c['location']['country']['code'] == u'gb' or 
              c['location']['country']['code'] == u'hu' or 
              c['location']['country']['code'] == u'it' or 
              c['location']['country']['code'] == u'be' or 
              c['location']['country']['code'] == u'de' or 
              c['location']['country']['code'] == u'bg' or 
              c['location']['country']['code'] == u'fr' or 
              c['location']['country']['code'] == u'dk' or 
              c['location']['country']['code'] == u'es' or
              c['location']['country']['code'] == u'se' or  
              c['location']['country']['code'] == u'no' or 
              c['location']['country']['code'] == u'pt' or 
              c['location']['country']['code'] == u'ie' or 
              c['location']['country']['code'] == u'hr' or 
              c['location']['country']['code'] == u'cz' or 
              c['location']['country']['code'] == u'lu' or 
              c['location']['country']['code'] == u'gr' or 
              c['location']['country']['code'] == u'pl'): nCountries['EU'] += 1
        else : nCountries['Other'] += 1

        transformed_location = c['location']['name']

        for transform in transforms:
            transformed_location = transformed_location.replace(*transform)
        # geo = g.geocode(transformed_location, exactly_one=False)
        # if geo == []: continue
        # results.update({ c['location']['name'] : geo })

        if 'Chicago' in c['location']['name']: nCities['Chicago'] += 1
        if 'San Francisco' in c['location']['name']: nCities['SF Bay'] += 1    

    #print json.dumps(results, indent=1)


##  ____  _       _   _                
## |  _ \| | ___ | |_| |_ ___ _ __ ___ 
## | |_) | |/ _ \| __| __/ _ \ '__/ __|
## |  __/| | (_) | |_| ||  __/ |  \__ \
## |_|   |_|\___/ \__|\__\___|_|  |___/
                                    
#############################################################
########## Pie chart of connection in various countries #####
#############################################################

from pylab import *

# make a square figure and axes
figure(1, figsize=(6,6), facecolor='white')
ax = axes([0.1, 0.1, 0.8, 0.8])


# The slices will be ordered and plotted counter-clockwise.
labels = 'US, Canada', 'CERN/Geneva', 'Rest of the world', 'Europe', 'India'

nTotal =  float( nCountries['US'] + nCountries['CERN'] + 
                 nCountries['Other'] + nCountries['EU'] + nCountries['India'])

fracs = [nCountries['US']/nTotal, nCountries['CERN']/nTotal, 
         nCountries['Other']/nTotal, nCountries['EU']/nTotal, 
         nCountries['India']/nTotal]
explode=(0, 0, 0.05, 0, 0)

pie(fracs, explode=explode, labels=labels,
    autopct='%1.1f%%', shadow=True)

title('Connections by geography', bbox={'facecolor':'0.8', 'pad':5})
savefig("conn_by_geography.png")
#show()


################# Histogram of connections################
from plotter import *
##### Connection : City 
BarChart(nCities.keys(), nCities.values(), 
         "Cities with >10 connections", "Connections", "conn_by_city.png")   

##### Connection : Profession
BarChart(nProf.keys(), nProf.values(), 
         "Professional areas", "Connections", "conn_by_prof.png")   

##### Connection : Healine word   
BarChart(nHline.keys(), nHline.values(), 
         "Most popular headline words", "Connections", "conn_by_headline.png")




