"""
Iterates over each faculty member's ORCID. 
Collects all publications from all faculty members.
Assembles them into a BibTeX file. 
"""


import requests
import json
import math
import pandas as pd
import random
import re
 

#ask for user input for upper and lower year constraints
start_year = int(input("Please enter a lower year limit: "))
end_year = int(input("Please enter an ending year limit: "))



link_lab_orcids = {
        'Negin Alemazkoor': '0000-0003-0221-3985',
        'Homa Alemzadeh': '0000-0001-5279-842X',          
        'Lawrence E. Band': '0000-0003-0461-0503',
        'Laura E. Barnes': '0000-0001-8224-5164',
        'Madhur Behl': '0000-0002-5921-0331',
        'Nicola Bezzo': '0000-0001-6627-5048',                 
        'Matthew Bolton': '0000-0002-3649-5637',
        'Steven Bowers': '0000-0002-4243-8663',
        'Maite Brandt-Pearce': '0000-0002-2566-8280',
        'Benton H. Calhoun': '0000-0002-3770-5050',
        'Brad Campbell': '0000-0002-4103-8107',
        'Qing Chang': '0000-0003-3744-1371',
        'T Donna Chen': '0000-0002-7026-3418',              
        'Seokhyun Chung': '0000-0001-5176-4180',
        'Haibo Dong': '0000-0001-7823-7014', 
        'Afsaneh Doryab': '0000-0003-1575-385X',          
        'Lu Feng': '0000-0002-4651-8441',       #?
        'Tomonari Furukawa': '0000-0003-2811-4221',
        'Gregory Gerling': '0000-0003-3137-3822',
        'Jonathan L. Goodall': '0000-0002-1112-4522',
        'Devin K. Harris': '0000-0003-0086-1073',
        'Seongkook Heo': '0000-0003-2004-4812',
        'Arsalan Heydarian': '0000-0001-5972-6947',
        'Tariq Iqbal': '0000-0003-0133-1234',
        'Yen-Ling Kuo': '0000-0002-6433-6713',               #?
        'Venkataraman Lakshmi': '0000-0001-7431-9004',
        'James H. Lambert': '0000-0002-0697-8339',
        'Zongli Lin': '0000-0003-1589-1443',
        'Felix Xiaozhu Lin': '0000-0002-1615-6419',
        'Zhen Liu': '0000-0001-8013-3804',                 
        'Eric Loth': '0000-0003-4113-733X',
        'Osman Ozbulut': '0000-0003-3836-3416',            
        'Byungkyu Brian Park': '0000-0003-4597-6368',
        'Daniel Quinn': '0000-0002-5835-5221',
        'Sara Riggs': '0000-0002-0112-9469',
        'Haiying Shen': '0000-0002-7548-6223',
        'Cong Shen': '0000-0002-3148-4453',
        'Brian Smith': '0000-0001-5102-6399',   #?
        'Mircea R. Stan': '0000-0003-0577-9976',
        'Yixin Sun': '0000-0001-6650-4373',
        'Ye Sun': '0000-0003-1086-8017',
        #'Shangtong Zhang': '0000-0003-4255-1364',
        #'N. Rich Nguyen': '0000-0002-4910-8069',
        #'Somayeh Asadi': '0000-0001-8868-5603',
        #'Kun Qian': '0000-0003-4971-8075',
    }



"""Step 1: Make API requests for data about each faculty member and their publications"""

# this holds each publication for all link lab faculty
all_publications_data = []

titles = []
authors = []    #author = "Orti, E. and Bredas, J.L. and Clarisse, C.",
dates = []
journals = []
urls = []

# landing_page_url

for name, orcid in link_lab_orcids.items():
    try:
        
        request = requests.get(f'https://api.openalex.org/authors/https://orcid.org/{orcid}')
        json_data = json.loads(request.text)


        #get URL from author info to get info about publications
        works_url_for_author = json_data['works_api_url']
        works_url_for_author = works_url_for_author.split("=")

        # get number of publications which will be used to find number of pages, for future API calls
        number_publications = json_data['works_count']
        number_of_pages = math.ceil(number_publications / 200)

        for i in range(number_of_pages):
            request2 = requests.get(f'https://api.openalex.org/works?filter={works_url_for_author[1]}&page={i+1}&per-page=200')
            json_data2 = json.loads(request2.text)

            print(json_data2)
    
            for pub in json_data2['results']:
                # take publications info and store in lists
                
                #first check if title contains chinese characters
                chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')  # Pattern to match Chinese characters
                
                if isinstance(pub['title'], str):  # for some reason, some of the titles are not strings?
                    if not chinese_pattern.search(pub['title']):
                        titles.append(pub['title'])
                
                
                
                        dates.append(pub['publication_year'])
                
                        # get journal title. Journal title not always available. If not available, just append "unknown journal"
                        try:
                            journals.append(pub['primary_location']['source']['display_name'])
                        except Exception:
                            journals.append('Unknown Journal')

                        # get jounal url's landing page
                        try:
                            urls.append(pub['primary_location']['landing_page_url'])
                        except Exception:
                            urls.append('Unknown URL')
                        
        
                        # must loop through authors to get each individual author for each publication. There can be many authors
                        authors_by_publication = []
                
                        for author in pub['authorships']:
                            author_name = author['author']['display_name']
                            authors_by_publication.append(author_name) 
                            
                        
                        # add group of authors_by_publication to authors list above
                        authors.append(authors_by_publication)
        
    except Exception:
        pass
    
    
    
# create dataframe to hold all publications data
df = pd.DataFrame()
# put lists above into columns
df['Title'] = titles
df['Author'] = authors
df['Date'] = dates
df['Journal'] = journals
df['Url'] = urls




# clean erroneous HTML tags from the titles
def remove_html_tags(text):
    # Regular expression pattern to match HTML tags
    pattern = r'<[^>]+>'
    
    # Use re.sub to replace HTML tags with an empty string
    clean_text = re.sub(pattern, '', text)
    
    return clean_text

def remove_html_tags_from_list(string_list):
    # Initialize an empty list to store strings without HTML tags
    strings_without_html_tags = []
    
    for text in string_list:
        clean_text = remove_html_tags(text)
        strings_without_html_tags.append(clean_text)
    
    return strings_without_html_tags

titles = remove_html_tags_from_list(titles)



# remove rows from dataframe that have a publication date outside the time frame previously established by the user in start_year and end_year
df = df[(df['Date'] >= start_year) & (df['Date'] <= end_year)]



"""Step 2: Create BibTeX file from pandas dataframe """


# Convert DataFrame to BibTeX format
bibtex_data = ""
count = 1
for index, row in df.iterrows():
    entry = f"@article{{{count},\n"
    
    # Join authors using 'and' separator
    authors = ' and '.join(row['Author'])
    entry += f"  author = {{{authors}}},\n"
    
    entry += f"  title = {{{row['Title']}}},\n"
    entry += f"  year = {{{row['Date']}}},\n"
    # if "Conference" in row['Journal']:
    #     entry += f"  conference = {{{row['Journal']}}},\n"
    # else:
    entry += f"  journal = {{{row['Journal']}}},\n"
    entry += f"  url = {{{row['Url']}}},\n"
    entry = entry.rstrip(',\n')  # Remove trailing comma and newline
    entry += "\n}\n\n"
    bibtex_data += entry

    count += 1


# Save to a .bib file
with open('Link_Lab_Publications.bib', 'w') as bibtex_file:
    bibtex_file.write(bibtex_data)
    






    



