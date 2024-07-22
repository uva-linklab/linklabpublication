from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
import os
import requests
#------------------------------------------------------------------

# This is the URL that the publication data is being fetched from. It is uploaded to bibbase after the bib file is update/generated
bibbase_url = "https://bibbase.org/show?bib=https://bibbase.org/f/Nu7vemBQmbYhdC97i/test.bib"

filter_years = ["2024","2023", "2022", "2021", "2020", "2019", "2018", "2017"]  



# List of Link Lab authors. Values are ORCID [0] and google scholar id [1]
author_ids = {
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
        'Lu Feng': '0000-0002-4651-8441',       
        'Tomonari Furukawa': '0000-0003-2811-4221',
        'Gregory Gerling': '0000-0003-3137-3822',
        'Jonathan L. Goodall': '0000-0002-1112-4522',
        'Devin K. Harris': '0000-0003-0086-1073',
        'Seongkook Heo': '0000-0003-2004-4812',
        'Arsalan Heydarian': '0000-0001-5972-6947',
        'Tariq Iqbal': '0000-0003-0133-1234',
        'Yen-Ling Kuo': '0000-0002-6433-6713',           
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
        'Brian Smith': '0000-0001-5102-6399',  
        'Mircea R. Stan': '0000-0003-0577-9976',
        'Yixin Sun': '0000-0001-6650-4373',
        'Ye Sun': '0000-0003-1086-8017',
        'Shangtong Zhang': '0000-0003-4255-1364',
        'N. Rich Nguyen': '0000-0002-4910-8069',
        'Somayeh Asadi': '0000-0001-8868-5603',
        'Kun Qian': '0000-0003-4971-8075',
}
#------------------------------------------------------------------

# This function creates the column of year and authors on the html page
def load_base_html():
    base_html = open("./base.html", "r").read()
    html = BeautifulSoup(base_html, "html.parser")
    column_html = BeautifulSoup(open("./column.html", "r").read(),'html.parser')
    return html, column_html

# This function formats the publications in html. It extracts the pre-formatted html from the bibbase URL- Bibbase formats the publications for us when we upload a bib file to the file manager
def get_bibbase_html(bibbase_url, filter_cond): 
    response = requests.get(f'{bibbase_url}&noBootstrap=1&authorFirst=1&filter={filter_cond}')
    # with open('body.html', 'r', encoding='utf-8') as file:
    #     html_content = file.read()
    r_html = response.text # get the response text. in this case it is HTML
    soup = BeautifulSoup(r_html, "html.parser") # parse the HTML
    body = soup.find('body')
    return body

# Creates the bare html file for years/authors
def create_and_init_html_file(filter):
    filter_html_file = open(f"./{filter}.html", "w")
    filter_bibbase = f'<h2 style="margin-bottom:20px;">{filter} Publications</h2> <div> </div>'
    filter_bibbase = BeautifulSoup(filter_bibbase, features="lxml")

    return filter_html_file, filter_bibbase

#------------------------------------------------------------------
#                                                                 #
#         The Link Lab Publications HTML Generator Starts         #
#                                                                 #
#------------------------------------------------------------------
"""Part 1/3: generate index.html !! -> USES 2024 PUBLICATIONS
"""
index_html_file = open("index.html", "w")
index_bibbase = f'<h2 style="margin-bottom:20px;">2024 Publications</h2> <div></div>'
index_bibbase = BeautifulSoup(index_bibbase, features="lxml")
bibbase_body = get_bibbase_html(bibbase_url, "year:2024")
tag = index_bibbase.div
tag.append(bibbase_body)

html, column_html = load_base_html()

html.find("div", class_= "index").insert(1,index_bibbase)
html.find("div", class_= "secondary_column").insert(1,column_html)
index_html_file.write(str(html.prettify()))
index_html_file.close()


""" Part 2/3: create year.html !!
"""
print("generating year_htmls_file")
for year in tqdm(filter_years):
    html, column_html = load_base_html()
    year_html_file, year_bibbase = create_and_init_html_file(year)

    bibbase_body = get_bibbase_html(bibbase_url, f"year:{year}")
    if bibbase_body is None:
        bibbase_body = '<span></span>'
    tag = year_bibbase.div
    tag.append(bibbase_body)

    html.find("div", class_= "index").insert(1,year_bibbase)
    html.find("div", class_= "secondary_column").insert(1,column_html)
    year_html_file.write(str(html.prettify()))
    year_html_file.close()

"""Part 3/3: create faculty.html !!
"""
print("generating faculty_htmls_file")
for name, (orcid) in tqdm(author_ids.items()):

    html, column_html = load_base_html()
    author_html_file, author_bibbase = create_and_init_html_file(name)
    bibbase_body = get_bibbase_html(bibbase_url, f"id:{orcid}") 

    if bibbase_body is None:
        bibbase_body = '<span></span>'
    tag = author_bibbase.div
    tag.append(bibbase_body)

    html.find("div", class_= "index").insert(1,author_bibbase)
    html.find("div", class_= "secondary_column").insert(1,column_html)
    author_html_file.write(str(html.prettify()))
    author_html_file.close()