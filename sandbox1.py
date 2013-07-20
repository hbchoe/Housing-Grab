'''
Created on Jul 13, 2013

@author: jcochran
'''

import urllib2
from bs4 import *
import html5lib
import re





"""
==============================================
HomePath
==============================================
"""

class homeRequest(object):
    
    def __init__(self):
        self.address_original = ""
        self.currentPage = 1
        self.nextPage = 1
        self.pages = {}
        self.params = {}
        
        """
        ---------------------------
        Default Values
        ---------------------------
        """
        
    '''
    =============================================== 
    Setters
    ===============================================        
    '''       

    def set_county(self,county):
        self.county = county
        
    def set_state(self,state):
        self.state = state
        
    def set_city(self,city):
        self.city = city
        
    def set_street(self,street):
        self.street = street
        
    def set_zip(self,zipcode):
        self.zipcode = zipcode
        
    def set_minPrice(self,minPrice):
        self.minPrice = minPrice
        
    def set_maxPrice(self,maxPrice):
        self.maxPrice = maxPrice
        
    def set_numBeds(self,numBeds):
        self.numBeds = numBeds
        
    def set_numBaths(self,numBaths):
        self.numBaths = numBaths
        
    def set_sqFt(self, sqFt):
        self.sqFt = sqFt
        
    def homePathRequest(self):
        #address = 'http://www.homepath.com/listing/search?loc=Portage%20County,%20OH&pg=1&pi=0&o=sscs&ps=10'
        #address = 'http://www.homepath.com/listing?listingid=39763341'
        #address = 'http://www.homepath.com/listing/search?loc=Portage%20County,%20OH&pg=1&pi=0&pa=50000&o=sscs&ps=2'
        address_original = 'http://www.homepath.com/listing/search?loc=Summit%20County,%20OH&pi=0&o=sscs&ps=10'
        
        
        
        currentPage = 1
        nextPage = 1
        pages = {}
        
        while currentPage != -1:
            address = address_original + "&pg={0}".format(str(currentPage))
            html = urllib2.urlopen(address).read()
            soup = BeautifulSoup(html,"html5lib")
            homes = {}
            currentPage = int(soup.find('input', id = "currentPageNumber").attrs['value'])
            nextPage = int(soup.find('input', id = "nextPageNumber").attrs['value'])
            print "NextPage: ", nextPage
            
            
            
            listings = soup.find_all('tr', id = re.compile("record_\d+"))
            for listing in listings:
                record = listing.attrs['id'].encode('latin-1')
                homes[record] = {}
                
                image = listing.find('a', attrs={"class": "tooltipImage"})
                homes[record]['image'] = image.attrs['rel'][0].encode('latin-1').encode('latin-1')
                homes[record]['page'] = "www.homepath.com" + image.attrs['href'].strip().encode('latin-1')
                
                    
                address = listing.find('a', attrs={"class": "address"})
                address = address.contents[0].strip() +  ", " + address.contents[2].strip()
                address = address.encode('latin-1')
                homes[record]['address'] = address
                
            
                bath = listing.find('p', attrs= {"class": "dgbath"})
                homes[record]['bath'] = bath.contents[0].strip().encode('latin-1')
                
                    
                bed = listing.find('p', attrs = {"class": "dgbed"})
                homes[record]['bed'] = bed.contents[0].strip().encode('latin-1')
                
                
                price = listing.find('p', attrs = {"class": "housePrice"})
                homes[record]['price'] = price.contents[0].strip().encode('latin-1')
                
            pages[currentPage] = homes.copy()
            currentPage = nextPage
        
        for page in pages.values():
            for home in page.values():
                print home['price']