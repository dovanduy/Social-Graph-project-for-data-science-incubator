import requests
from bs4 import BeautifulSoup
import re

def write_list_to_file(filename, list_to_write):
    """
    Saves list contents to a file
    """
    inFile=open(filename,'w')
    string_list=[]
    for i in range(0,len(list_to_write)):
        string_list.append(str(list_to_write[i])) 
    inFile.write('\n'.join(string_list))
    inFile.close()

def load_file_as_list(filename):
    """
    returns file contents as a list where each line is a element of the list
    """
    inFile = open(filename)
    lines = inFile.readlines()
    inFile.close()
    return lines

partypicsurl="http://www.newyorksocialdiary.com/party-pictures" #example of a full url: http://www.newyorksocialdiary.com/party-pictures/2007/orchids-growing-wild
target_divs=[]

for page_num in range(0,28):
    response=requests.get(partypicsurl, params={"page":page_num})
    soup = BeautifulSoup(response.text, "html.parser")
    target_divs = target_divs + soup.find_all('div', attrs={'class': 'views-row'}) 
              
dates_n_urls=[]
for index, item in enumerate(target_divs):
    date = re.search('\w+, (\w+) \d+, (\d\d\d\d)', item )
    if date!=None:
        corresp_url=re.search('/[^">]*', target_divs[index-1] )
        if corresp_url==None:
            raise ValueError("No URL found")
    
        # need only pics before December 1st, 2014 per project goal
        if (int(date.group(2))<2014) or ((int(date.group(2))==2014) and (date.group(1)!="December")):
            dates_n_urls.append((date.group(0),'http://www.newyorksocialdiary.com'+corresp_url.group()))
            
write_list_to_file("onlyurls.txt", [it[1] for it in dates_n_urls]) 

selected_urls  = [it[1] for it in dates_n_urls]
for item in selected_urls:
    print item
