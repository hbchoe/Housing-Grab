'''
Created on Jul 13, 2013

@author: jcochran
'''

import urllib2, re, pickle, os, smtplib
from bs4 import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders





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
        self.recipients = None
        self.sender = ""
        self.emailMsg = None
        self.emailWrapper = None
        self.homesList = []
        self.message = ""
        
        """
        ---------------------------
        Addresses
        ---------------------------
        """
        self.homePathAddress = "http://www.homepath.com"
        
    '''
    =============================================== 
    Override rich operators
    ===============================================        
    '''       
        
    def __eq__(self,other):
        try:
            return self.pages == other.pages
        except AttributeError:
            return False
    
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
        
        
    '''
    ==============================================
    Request Compilers
    ==============================================
    '''
        
        
        
    def compileHomePathRequest(self):
        self.currentAddress = self.homePathAddress
        self.searchAddress = self.currentAddress + "/listing/search?"
        words = re.compile("(\w+)")
        
        # Isolate State
        found = words.match(self.state)
        stateName = found.group(1).upper()
        try:
            assert(len(stateName) == 2)
        except AssertionError:
            print "Please enter the abbreviation for your state"
        
        # Isolate County
        try:
            found = words.match(self.county)
            countyName = found.group(1)
        except AttributeError:
            print "No county"
        
        # Isolate City
        try:
            found = words.match(self.city)
            cityName = found.group(1).lower()
        except AttributeError:
            print "No city"
        
        #c Compile City, State Query
        #cityAddendum = "loc=" + cityName + ",%20" + stateName
        
        # Compile County, State Query
        countyAddendum = "loc=" + countyName + "%20" + "County," + "%20" + stateName
        
        # Addend Current Address
        self.searchAddress += countyAddendum
        
    def compileTextCell(self,home):
        textCell = """
        Home Stats <br>
        ======================== <br>
        Price: %s <br>
        Address: %s <br> 
        Beds: %s <br>
        Baths: %s
        """ % (home['price'],home['address'],home['bed'],home['bath'])
        
        return textCell
            
    
    def compileImageCell(self,home):
        #print type(home['page']), type(home['image'])
        imageCell = "<a href=\"%s\"><img src=\"%s\" style=\"width:100%%\"></a>" % (home['page'],home['image'])
        
        return imageCell
    
    def compileRow(self,home):
        row = """
                    <tr>
                        <td style="width:250px"> %s </td>
                        <td> %s </td>
                    </tr>
        """ % (self.compileImageCell(home), self.compileTextCell(home))
        return row
    
    def compileTable(self,partialHomeList):
        table = """
                <table border=3 style="width:800px">
        """
        for home in partialHomeList:
                table += self.compileRow(home)
                
        table += """
                </table>
        """
        return table
    
    def compileHomesList(self):
        tempHomeList = []
        for page in self.pages.values():
            for home in page.values():
                tempHomeList.append(home)
        
        tempHomeList = sorted(tempHomeList, key=lambda home: int(home['price'][1:].replace(',', '')))
        self.homesList =  tempHomeList
    
    
    
    '''
    ==========================================
    Types of Requests
    ==========================================
    '''
    
    def makeCountyRequest(self,county,state):
        self.set_county("%s" % county)
        self.set_state("%s" % state)
        self.homePathRequest()
        self.add_subject('Update on homes in %s County, %s' % (self.county,self.state))
        self.set_sender('foreclosuresoverknives@gmail.com')
        self.add_recipient('koenigcochran@gmail.com')
        self.add_message('The status of the following homes has changed:\n')
        self.sendResults()
    
    '''
    ==========================================
    Page Requests
    ==========================================
    '''
        
    def homePathRequest(self):    
        
        #address = 'http://www.homepath.com/listing/search?loc=Portage%20County,%20OH&pg=1&pi=0&o=sscs&ps=10'
        #address = 'http://www.homepath.com/listing?listingid=39763341'
        #address = 'http://www.homepath.com/listing/search?loc=Portage%20County,%20OH&pg=1&pi=0&pa=50000&o=sscs&ps=2'
        #address_original = 'http://www.homepath.com/listing/search?loc=Summit%20County,%20OH&pi=0&o=sscs&ps=10'
        
        self.compileHomePathRequest()

        while self.currentPage != -1:
            address = self.searchAddress + "&pg={0}".format(str(self.currentPage))
            html = urllib2.urlopen(address).read()
            soup = BeautifulSoup(html,"html5lib")
            homes = {}
            print address
            self.currentPage = int(soup.find('input', id = "currentPageNumber").attrs['value'])
            self.nextPage = int(soup.find('input', id = "nextPageNumber").attrs['value'])
            #print "NextPage: ", self.nextPage
            
            
            
            listings = soup.find_all('tr', id = re.compile("record_\d+"))
            for listing in listings:
                record = listing.attrs['id'].encode('latin-1')
                homes[record] = {}
                
                image = listing.find('a', attrs={"class": "tooltipImage"})
                homes[record]['image'] = image.attrs['rel'][0].encode('latin-1').encode('latin-1')
                homes[record]['page'] = "www.homepath.com" + image.attrs['href'].strip().encode('latin-1')
                
                    
                streetAddress = listing.find('a', attrs={"class": "address"})
                streetAddress = streetAddress.contents[0].strip() +  ", " + streetAddress.contents[2].strip()
                streetAddress = streetAddress.encode('latin-1')
                homes[record]['address'] = streetAddress
                
            
                bath = listing.find('p', attrs= {"class": "dgbath"})
                homes[record]['bath'] = bath.contents[0].strip().encode('latin-1')
                
                    
                bed = listing.find('p', attrs = {"class": "dgbed"})
                homes[record]['bed'] = bed.contents[0].strip().encode('latin-1')
                
                
                price = listing.find('p', attrs = {"class": "housePrice"})
                if price.contents[0].strip().encode('latin-1') != '':
                    homes[record]['price'] = price.contents[0].strip().encode('latin-1')
                    
                else:
                    homes[record]['price'] = '$0'
                
            self.pages[self.currentPage] = homes.copy()
            self.currentPage = self.nextPage
                
                
    """
    ==============================
    EMail
    ==============================
    """
    def add_recipient(self,recipient):
        if self.recipients is None:
            self.recipients = [recipient]
        else:
            self.recipients.append(recipient)
        
    def set_sender(self,sender):
        self.sender = sender
        
    def add_subject(self,subject):
        self.subject = subject
        
    def add_message(self,message):
        self.message = message
        
    def composeHTML(self,partialHomeList):
        
        htmlmsg = """\
        <html>
            <head></head>
            <body>
        %s
            </body>
        </html>
        """ % (self.compileTable(partialHomeList))
        
        return htmlmsg
        
    def composeEmail(self,partialHomeList):
        self.emailMsg            = MIMEMultipart()
        self.emailMsg['Subject'] = self.subject
        self.emailMsg['From']    = self.sender
        self.emailMsg['To']      = ', '.join(self.recipients)
        
        text = self.message
        htmlmsg = self.composeHTML(partialHomeList)
        #print htmlmsg
        
        part1 = MIMEText(text,'plain')
        part2 = MIMEText(htmlmsg,'html')
        
        self.emailMsg.attach(part1)
        self.emailMsg.attach(part2)
    
    def sendEmail(self):
        self.emailWrapper = smtplib.SMTP('smtp.gmail.com', 587)
        self.emailWrapper.ehlo()
        self.emailWrapper.starttls()
        self.emailWrapper.ehlo
        self.emailWrapper.login('foreclosuresoverknives@gmail.com','1lkjflkjf1')
        self.emailWrapper.sendmail(self.sender, self.recipients, self.emailMsg.as_string())
        self.emailWrapper.quit()
        
    def sendResults(self):
        self.compileHomesList()
        numHomes = len(self.homesList)
        
        
        if numHomes > 25:
            
            lower = 0
            upper = 25
            
            self.add_message('(The number of updates exceeds 25. An exhaustive list of updates is included as an attachment)\n')
            self.composeEmail(self.homesList[lower:upper])

            fileName = self.subject.replace(' ','') + '.html'
            htmlmsg = self.composeHTML(self.homesList)
            htmlFile = open(fileName,'wb')
            htmlFile.write(htmlmsg)
            htmlFile.close()
            
            htmlFile = open(fileName,'rb')
            part = MIMEBase('application', "octet-stream")
            part.set_payload( htmlFile.read() )
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(fileName))
            self.emailMsg.attach(part)
        
        else:
            lower = 0
            upper = numHomes
            self.composeEmail(self.homesList[lower:upper])
        
        
        self.sendEmail()
            
                
    '''
    =======================================
    Load / Save / Compare
    =======================================
    '''
    
    def saveResults(self):
        try:
            assert(len(self.homesList) != 0)
        except AssertionError:
            print "No search results to save"
        
        print self.homesList[-1]
        
        fileName = self.county + self.state + '.pkl'
        saveFile = open(fileName,'wb')
        
        pickle.dump(self, saveFile)
        
    def loadResults(self):
        try:
            fileName = self.county + self.state + '.pkl'
            loadFile = open(fileName,'rb')
            oldData = pickle.load(loadFile)
        except IOError:
            #print "Initializing..."
            oldData = self

        return oldData
    
    def compareResults(self):
        oldHomes = self.loadResults().homesList
        newHomes = self.homesList
        
        
    
if __name__ == "__main__":
    testCase1 = homeRequest()
    testCase2 = homeRequest()
    testCase3 = homeRequest()
    testCase4 = homeRequest()
    
    testCase1.makeCountyRequest('Portage', 'OH')
    testCase2.makeCountyRequest('Summit', 'OH')
    testCase3.makeCountyRequest('Medina', 'OH')
    testCase4.makeCountyRequest('Cuyahoga', 'OH')



    
    
    #testCase.saveResults()
    #nextGuy = testCase.loadResults()