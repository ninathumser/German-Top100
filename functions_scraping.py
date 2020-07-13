# Standard libraries
import datetime as dt
from random import randint
import re
import time

# Other libraries
from IPython.core.display import clear_output
from bs4 import BeautifulSoup
from itertools import repeat
import numpy as np
import pandas as pd
import requests
from warnings import warn



def select_pages(start_date='2019-01-01', end_date='2019-12-31'):
    root_url = 'https://www.offiziellecharts.de/charts/single/for-date-'
    date_1976_12_31 = 220834800000             #page_id of 31/12/1976
    
    start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
    
    if start_date < dt.datetime(1976, 12, 31):
        page_start = date_1976_12_31
    else:
        distance_start = (start_date - dt.datetime(1976, 12, 31)).days
        page_start = date_1976_12_31 + (distance_start * 86400000)   #one daily page_id is 86400000 away from the next daily page_id

    distance_end = (end_date - dt.datetime(1976, 12, 31)).days
    page_end = date_1976_12_31 + (distance_end * 86400000)
    
    pages = list(range(page_start, page_end, 86400000*7))
    
    return pages




def crawl_charts(pages):
    # Initiate empty lists for items of interest
    artists = []
    end_dates = []
    labels = []
    positions = []
    songs = []
    sources = []
    start_dates = []
    
    # Preparing the monitoring of the loop
    request = 0
    start_time = time.time()
    
    for page in pages:
        # Make a get request
        root_url = 'https://www.offiziellecharts.de/charts/single/for-date-'
        response = requests.get(root_url + str(page))
        sources.append(root_url + str(page))

        # Pause the loop
        time.sleep(randint(8,15))

        # Monitor the requests
        request += 1
        elapsed_time = time.time() - start_time
        print('Request:{}; Frequency: {} requests/s'.format(request, request/elapsed_time))
        clear_output(wait = True)

        # Throw a warning for non-200 status codes
        if response.status_code != 200:
            warn('Request: {}; Status code: {}'.format(request, response.status_code))

        # Break the loop if the number of requests is greater than expected (list of pages)
        if request > len(pages):
            warn('Number of requests was greater than expected.')
            break

        # Parse the content of the request with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')


        # Select all the 100 song containers from a single page
        containers = soup.find_all('tr', class_ = 'drill-down-link')

        # For every song of these 100 songs
        for container in containers:
             # Scrape the artist
            artist = container.find('span', class_ = 'info-artist').text
            artists.append(artist)

            # Scrape the song
            song = container.find('span', class_ = 'info-title').text
            songs.append(song)

            # Scrape the label
            label = container.find('span', class_ = 'info-label').text
            labels.append(label)

            # Scrape the chart position
            position = container.find('span', class_ = 'this-week').text
            positions.append(position)
              
        # Scrape start and end date of the week
        date = soup.find("span", class_='ch-header').text
        start_date = re.findall(r'(\d+\.\d+\.\d+)', date)[0]
        end_date = re.findall(r'(\d+\.\d+\.\d+)', date)[1]
        max_pos = int(positions[-1])                      # determining the length of the charts (Top50, Top75, Top100)
        start_dates.extend(repeat(start_date, max_pos))   # adding date x times to to the list (x=length of topX list)
        end_dates.extend(repeat(end_date, max_pos))
            
    # Create pandas dataframe
    charts = pd.DataFrame({'artist': artists,
                       'song': songs,
                       'label': labels,
                       'position': positions,
                       'start_date': start_dates,
                       'end_date': end_dates
                      })
        
    return charts


def create_file(df, filename):
    df.to_pickle(filename)