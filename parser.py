#-------------------------------------
# Import Modules
#-------------------------------------
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import csv
import re
import datetime
from requests.exceptions import ProxyError

#-------------------------------------
# Define Table headers
#-------------------------------------
table_headers = ['ID','PreisProQM','Added here','Link','Zimmer','Schlafzimmer','Badezimmer','Wohnfläche ca.','Gesamtmiete',
                 'Kaltmiete','Grundriss','Stadtteil','Address','Etage','Objektzustand','Bezugsfrei ab','Typ','Nutzfläche ca.',
                 'Nebenkosten','Heizkosten','Ausstattung','Baujahr','Besonderheiten','Bonitätsauskunft','Endenergiebedarf',
                 'Energieausweis','Energieausweistyp','Energieeffizienzklasse','Energieverbrauchskennwert',
                 'Garage/ Stellplatz','Haustiere','Heizungsart','Internet','Modernisierung/ Sanierung',
                 'Wesentliche Energieträger']

#-------------------------------------
# Set up Variables
#-------------------------------------
ua = UserAgent()

#-------------------------------------
# Fetch Data
#-------------------------------------
class PropertyParser():

    def __init__(self, sdate):
        self.sdate = sdate

    def define_request(self, url, proxy):
        headers = {'User-Agent': ua.random}
        proxies = {'http':proxy, 'https':proxy}
        res = requests.get(url, proxies=proxies, headers=headers)
        if res.ok:
            return res.text
        else:
            raise ProxyError('The request did not get through: ', res)

    def parse_url(self, html):
        soup = BeautifulSoup(html, 'lxml')
        return soup

    def check_content(selfs,soup):
        results = soup.find_all('li', attrs={'class':'result-list__listing '})
        if len(results) == 0:
            raise IndexError('There are no more listings on this page')
        else: pass

    # FOR ALL PROPERTIES
    def link_list(self, soup):
        id_key = 'data-go-to-expose-id'
        id_list = [x[id_key] for x in
                     soup.find_all('a', attrs={'class': 'result-list-entry__brand-logo-container'})
                     if id_key in x.attrs]
        return id_list

    # FOR INDIVIDUAL PROPERTIES
    def retrieve_address(self, soup):
        address = soup.find('div', attrs={'class':'address-block'}).text.strip(' ')
        try:
            borough = re.findall(r'(?<=\()[\w\s]+(?=\))', address)[0]
        except:
            borough = 'Unknown'
        self.address_dict = dict(Address= address, Stadtteil=borough)

    def retrieve_features(self, soup):
        feature_tag = soup.find('div',attrs={'class':'criteriagroup boolean-listing padding-top-l'})
        try:
            features_ = [f.text for f in feature_tag.find_all('span')]
            features = ', '.join(features_)
        except: features = 'Keine Besonderheiten'
        self.feature_dict = dict(Besonderheiten=features)

    def retrieve_flatdims(self, soup):
        ramble = soup.find('div', attrs={'class': 'criteriagroup criteria-group--two-columns'})
        dims_list = ramble.find_all('dl', attrs={'class':'grid'})
        dim_keys = [x.find('dt').text.strip() for x in dims_list]
        dim_values = [x.find('dd').text.strip() for x in dims_list]
        flatdims_dict = dict(zip(dim_keys,dim_values))
        # Clean sm values
        try:
            flatdims_dict['Wohnfläche ca.'] = re.findall(r'[\d\,]+', flatdims_dict['Wohnfläche ca.'])[0].replace(',','.')
        except: pass
        try:
            flatdims_dict['Nutzfläche ca.'] = re.findall(r'[\d\,]+', flatdims_dict['Nutzfläche ca.'])[0].replace(',','.')
        except: pass
        self.flatdims_dict = flatdims_dict

    def retrieve_costs(self, soup):
        keys = ['Kaltmiete','Nebenkosten','Heizkosten','Gesamtmiete']
        try:
            # Kaltmiete
            bare_text = soup.find('dd',attrs={'class':'is24qa-kaltmiete grid-item three-fifths'}).text.strip(' ')
            try:
                bare_rent = re.findall(r'[\d\.]+', bare_text)[0].replace('.','')
            except: bare_rent = bare_text
            # Nebenkosten
            utilities_text = soup.find('dd',attrs={'class':'is24qa-nebenkosten grid-item three-fifths'}).text.strip(' ')
            try:
                utilities = re.findall(r'[\d\.]+', utilities_text)[0].replace('.','')
            except: utilities = utilities_text
            # Heizkosten
            heating_text = soup.find('dd',attrs={'class':'is24qa-heizkosten grid-item three-fifths'}).text.strip(' ')
            try:
                heating_costs = re.findall(r'[\d\.]+', heating_text)[0].replace('.','')
            except: heating_costs = heating_text
            # Gesamtmiete
            full_text = soup.find('dd',attrs={'class':'is24qa-gesamtmiete grid-item three-fifths font-bold'}).text.strip(' ')
            try:
                full_rent = re.findall(r'[\d\.]+', full_text)[0].replace('.','')
            except: full_rent = full_text
            self.cost_dict = dict(zip(keys, [bare_rent, utilities, heating_costs, full_rent]))
        except AttributeError:
            self.cost_dict = dict()

    def retrieve_building(self, soup):
        ramble = soup.find('div', attrs={'class':"criteriagroup criteria-group--border " \
                                                 "criteria-group--two-columns criteria-group--spacing"})
        try:
            ramble_keys = ramble.find_all('dt')
            ramble_values = ramble.find_all('dd')
            key_list = [x.text.replace(u'\xad', '') for x in ramble_keys]
            value_list = [x.text.strip() for x in ramble_values]
            self.building_dict = dict(zip(key_list,value_list))
        except AttributeError:
            self.building_dict = dict()

    def retrieve_floorplan(self, soup):
        plan_link = soup.find_all('div', attrs={'class':'is24-text is24-ex-floorplan'})
        plan_button = soup.find_all('button', attrs={'data-qa':'grundriss_button'})
        if len(plan_link) == 0 and len(plan_button) == 0:
            plan_existence = 'No'
        else:
            plan_existence = 'Yep'
        self.floorplan_dict = dict(Grundriss=plan_existence)

    def write_object(self):
        full_dict = {**self.address_dict, **self.feature_dict, **self.flatdims_dict, **self.cost_dict,
                     **self.building_dict, ** self.floorplan_dict}
        return(full_dict)

    def fill_table(self, full_dict, id, sdate):
        # Reorder Values to fit into csv
        dict_values = []
        # Build up some extra values and identifiers
        dict_values.append(id)
        pricesm = round(float(full_dict['Gesamtmiete'])/float(full_dict['Wohnfläche ca.']), 2)
        dict_values.append(pricesm)
        date_added = f"{datetime.datetime.now():%m_%d}"
        dict_values.append(date_added)
        link = 'https://www.immobilienscout24.de/expose/' + id
        dict_values.append(link)
        # Prep for final insert
        full_dict['Zimmer'] = full_dict['Zimmer'].strip().replace(',', '.')
        # Reshuffle dictionary values according to csv table
        for key in table_headers[4:]:
            if key in full_dict.keys():
                dict_values.append(full_dict[key])
            else:
                dict_values.append('KA')
        # Save files into individual scrape file
        csv_file = open('/home/ubuntu/dataANDtoolbox/scrape-wgs/dataset/'
                        'individual_scrape/properties_{}.csv'.format(sdate),'a', encoding='latin-1')
        writer = csv.writer(csv_file)
        writer.writerow(dict_values)
        csv_file.close()
