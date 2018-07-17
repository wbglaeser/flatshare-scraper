#-------------------------------------
# Import Modules
#-------------------------------------
import time
import csv
import datetime
import combine
from random import randint
from itertools import cycle
from requests.exceptions import ProxyError, SSLError, ChunkedEncodingError

# My own modules
from parser import PropertyParser
from proxies import ProxyScrawler

def main_func():
    #-------------------------------------
    # Collect Proxies from SLL PROXY LIST
    #-------------------------------------
    proxy = ProxyScrawler()
    proxy_dict = proxy.return_proxy_dict()
    proxy_list = [e['ip'] + ':' + e['port'] for e in proxy_dict]
    proxy_pool = cycle(proxy_list)
    proxy = next(proxy_pool)

    #-------------------------------------
    # CONFIGURE SCRIPT
    #-------------------------------------
    table_headers = ['ID','PreisProQM','Added here','Link','Zimmer','Schlafzimmer','Badezimmer','Wohnfläche ca.','Gesamtmiete',
                 'Kaltmiete','Grundriss','Stadtteil','Address','Etage','Objektzustand','Bezugsfrei ab','Typ','Nutzfläche ca.',
                 'Nebenkosten','Heizkosten','Ausstattung','Baujahr','Besonderheiten','Bonitätsauskunft','Endenergiebedarf',
                 'Energieausweis','Energieausweistyp','Energieeffizienzklasse','Energieverbrauchskennwert',
                 'Garage/ Stellplatz','Haustiere','Heizungsart','Internet','Modernisierung/ Sanierung',
                 'Wesentliche Energieträger']

    sdate = f"{datetime.datetime.now():%m_%d_%H_%M}"

    #-------------------------------------
    # Fetch List of Properties
    #-------------------------------------
    '''This part of the code goes through the listing pages and obtains a unique id for each property. This id will
    allow us to follow the link to the webpage of the individual property.'''
    parser = PropertyParser(sdate)
    listings_ids_full = []
    idx = 1
    for i in range(1,30):
        try:
            listings_url = 'https://www.immobilienscout24.de/Suche/S-T/P-{}/Wohnung-Miete/Berlin/Berlin/Kreuzberg-' \
                       'Kreuzberg_Mitte-Mitte_Neukoelln-Neukoelln_Prenzlauer-Berg-Prenzlauer-Berg_Wedding-Wedding/' \
                       '3,00-/-/EURO--1600,00?enteredFrom=result_list'.format(idx)  # Define url
            listings_html = parser.define_request(listings_url, proxy)
            listings_soup = parser.parse_url(listings_html)
            parser.check_content(listings_soup)
            listings_ids = parser.link_list(listings_soup)
            listings_ids_full.extend(listings_ids)   #
            print('Page {} scraped for IDs.'.format(idx))
            idx += 1
        except (ProxyError, SSLError, ChunkedEncodingError) as e:     # BAD PROXY
            proxy = next(proxy_pool)
            print('We have a bad proxy.')
        except IndexError as e:
            print(e, idx)
            break

    #-------------------------------------
    # CLEAN IDS
    #-------------------------------------
    # Delete duplicate catches
    listings_ids_full = list(set(listings_ids_full))

    # Delete those that have been scrape before
    already_scraped = []
    with open('/home/ubuntu/dataANDtoolbox/scrape-wgs/dataset/property_ids_full.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            already_scraped.append(line.strip('\n'))
    property_ids_new = [i for i in listings_ids_full if i not in already_scraped]
    print('{} new properties will be scraped.'.format(len(property_ids_new)))
    # Only from individual scrape
    with open('/home/ubuntu/dataANDtoolbox/scrape-wgs/dataset/'
              'individual_scrape/properties_{}.csv'.format(sdate), 'w', encoding='latin-1') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(table_headers)

    #-------------------------------------
    # OBTAIN THE JUICY INFORMATION
    #-------------------------------------
    idx2 = 0
    failed_ids = []
    #scrape_ids = all_property_ids
    scrape_ids = property_ids_new

    # LOOP
    for i in range(200):
        if idx2 <= len(scrape_ids)-1:

            #---------------------------------
            # SCRAPE
            #---------------------------------
            try:
                # Obtain HTML
                property_url = 'https://www.immobilienscout24.de/expose/' + scrape_ids[idx2]
                property_html = parser.define_request(property_url, proxy)

                # Random Sleep
                time.sleep(randint(5, 10) * 0.25)

                # Parse, scrape and store information
                property_soup = parser.parse_url(property_html)
                parser.retrieve_address(property_soup)
                parser.retrieve_features(property_soup)
                parser.retrieve_costs(property_soup)
                parser.retrieve_flatdims(property_soup)
                parser.retrieve_building(property_soup)
                parser.retrieve_floorplan(property_soup)
                full_dict = parser.write_object()
                parser.fill_table(full_dict, scrape_ids[idx2], sdate)
                idx2 += 1
                print('Object retrieved')
            except (ProxyError, SSLError, ChunkedEncodingError) as e:     # BAD PROXY
                proxy = next(proxy_pool)
                print('We have a bad proxy.')

        else:
            print('All properties have been scraped')
            break

    #-------------------------------------
    # Save scraped ids
    #-------------------------------------
    with open('/home/ubuntu/dataANDtoolbox/scrape-wgs/dataset/property_ids_full.txt', 'w', encoding='utf-8') as f:
        for id in listings_ids_full:
            f.write(id + '\n')

    #-------------------------------------
    # Combine with existings files and save
    #-------------------------------------
    combine.main_func()
