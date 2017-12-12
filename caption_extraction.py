import requests
import bs4
import re
from ediblepickle import checkpoint
import sys
import time
from bs4 import *

def write_unicode_list_to_file(SEQUENCE_FILENAME, list_to_write):
    """
    Writes list (list_to_write) into a file SEQUENCE_FILENAME where each element of the list is written into the new line
    Previous content of the file (if any) is deleted)
    Converts all elements of list_to_write to strings using str() function.
    """
    inFile=open(SEQUENCE_FILENAME,'w')
    string_list=[]
    for i in range(0,len(list_to_write)):
        string_list.append(str(list_to_write[i].encode('utf8')))
    
    inFile.write('\n'.join(string_list))
    inFile.close()

def load_unicode_file_as_list(filename_to_load):
    """
    returns file contents as a list where each line is a element of the list
    """
    inFile = open(filename_to_load)
    lines = inFile.readlines()
    lines = [line.decode('utf8') for line in lines]
    lines = [line.replace('\n','') for line in lines]
    inFile.close()
    return lines


#@checkpoint('allrequestsget.csv', refresh = False) #DON"T FORGET TO SET REFRESH=TRUE IF YOU'RE CHANGING SOMETHING
def grab_responses():
    picurls=load_unicode_file_as_list('onlyurls.txt')
    picurls=[line.replace('\n','') for line in picurls]
    all_responses = []
    for index, picurl in enumerate(picurls):
        time.sleep(0.5)
        print 'grabbing responses from # %i url: %s' %(index,picurl)
        try:
            response=requests.get(picurl)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print e
            time.sleep(15)
            try:
                response=requests.get(picurl)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print 'Still no luck with this url. Continuing anyway'

        all_responses.append(response)
    return all_responses

#@checkpoint('allcaptiontags.csv', refresh=False) #DON"T FORGET TO SET REFRESH=TRUE IF YOU'RE CHANGING SOMETHING
def grabbing_soup(responses):
    parser="html.parser" #can use "lxml" or "html.parser", whatever works better
    caption_divs=[]
    for index, response in enumerate(responses):
        print 'soupifying from # %i ths response' %index
        newFormat=False
        soup = BeautifulSoup(response.text, parser)
        temp_divs=soup.find('div',attrs={'class':'field__items'})
        tempdivs=[]
        for section in temp_divs.findAll('table'):
            newdivs = None
            
            newdivs=section.find_all('div', attrs={'class':'photocaption'}) #soup->section
            if len(newdivs) > 0:
                newFormat = True
                tempdivs += newdivs
                    
            else:
                newdivs = None
                newdivs = section.find_all('td', attrs={'class':'photocaption'}) #soup->section
                #e.g. this picture has photocaptions in td, not in divs: http://www.newyorksocialdiary.com/party-pictures/2013/spring-gala-galore
                #warning - in td: both td with pic and a lower td with caption are labeld photocaption - need to get rid of td photocaptions with img src tag
                if len(newdivs) > 0:
                    newFormat = True
                    tempdivs += newdivs
                        
                else:
                    newdivs = None
                    newdivs = section.find('font', attrs={'size':1})
                    if newdivs != None:      
                        tempdivs += newdivs

            
        print 'format for this page is new?:', newFormat

        new_caption_divs=list(set(tempdivs)) #will be unordered

        caption_divs = caption_divs + new_caption_divs
    return caption_divs

@checkpoint('captions_extr_init_html.csv', refresh=False) #DON"T FORGET TO SET REFRESH=TRUE IF YOU'RE CHANGING SOMETHING
def captions_extract(caption_divs):
    captions = []
    print' total number of els in caption_divs: %i' %len(caption_divs)
    for el in caption_divs:
        if type(el) == bs4.element.NavigableString:
            text_to_strip = el
        elif type(el) == bs4.element.Tag:
            text_to_strip = el.text
        elif type(el) == bs4.element.Comment:
            text_to_strip = el 
        temp=re.sub( '\s+', ' ', text_to_strip).strip()
        if len(temp) > 3 and len(temp) <= 250: #pick elements likely to be actual captions
            captions.append(temp)
            

    print 'length of captions list= %i' %len(captions)
    return captions
      

responses = grab_responses()
print 'responses grabbed. Starting souppifying...'

caption_divs = grabbing_soup(responses)
captions = captions_extract(caption_divs)
write_unicode_list_to_file("captions.txt", captions)
