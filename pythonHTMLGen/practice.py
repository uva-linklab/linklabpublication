from bs4 import BeautifulSoup
from pathlib import Path
import os
import requests

#
bibbase_url = "https://bibbase.org/show?bib=https://bibbase.org/f/fFERMKNwKyHLsDPJ3/Link_Lab_Publications.bib"
# 
filter_years = ["2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015"]  
# 
filter_authors = {
   "Negin Alemazkoor": "Alemazkoor, N.",
   "Homa Alemzadeh": "Alemzadeh, H.",
   "Lawrence E. Band": "Band, L. E.",
   "Laura E. Barnes": "Barnes, L. E.",
   "Madhur Behl": "Behl, M.",
   "Nicola Bezzo": "Bezzo, N.",
   "Matthew Bolton": "Bolton",
   "Steven Bowers": "Bowers",
   "Maite Brandt-Pearce":  "Brandt-Pearce",
   "Benton H. Calhoun": "Calhoun",
   "Brad Campbell": "Campbell, B.",
   "Qing Chang": "Chang, Q.",
   "Donna T. Chen": "Chen, T. D.",
   "Seokhyun Chung": "Chung",
   "Haibo Dong": "Dong",
   "Afsaneh Doryab": "Doryab, A.",
   "Lu Feng": "Lu, F.",
   "Tomonari Furukawa": "Furukawa, T.",
   "Gregory J. Gerling": "Gerlin",
   "Jonathan L. Goodall": "Goodall, J. L.",
   "Devin K. Harris": "Harris, D.",
   "Seongkook Heo": "Heo, S.",
#
   "Arsalan Heydarian": "Heydarian, A.",
   "Tariq Iqbal": "Iqbal, T.",
   "Yen-Ling Kuo": "Kuo",
   "Venkataraman Lakshmi": "Lakshmi, V.",
   "James H. Lambert": "Lambert",
   "Zongli Lin": "Lin, Z.",
   "Felix Xiaozhu Lin": "Lin",
   "Zhen Liu": "Liu",
   "Eric Loth": "Loth, E.",
   "Osman E. Ozbulut": "Ozbulut, O. E.",
   "Byungkyu Brian Park": "Park, B. B.",
   "Daniel Quinn": "Quinn, D.",
   "Sara L. Riggs": "Riggs, S",
   "Haiying Shen": "Shen, H.",
   "Cong Shen": "Shen, C.",
   "Brian Smith": "Smith, B.",
   "Mircea R. Stan": "Stan, M. R.",
   "Yixin Sun": "Sun, Y.",
   "Ye Sun": "Sun, Y.",
}
#
filter_theme = {}

base_html = open("./base.html", "r").read()
html = BeautifulSoup(base_html, "html.parser")
column_html = BeautifulSoup(open("./column.html", "r").read(),'html.parser')

# create index.html !!
index_html_file = open("index.html", "w")
index_bibbase = f'<h2 style="margin-bottom:20px;">2023 Publications</h2> <script src={bibbase_url}&noBootstrap=1&jsonp=1&authorFirst=1&filter=year:2023></script>'
index_bibbase = BeautifulSoup(index_bibbase, features="lxml")


html.find("div", class_= "index").insert(1,index_bibbase)
html.find("div", class_= "secondary_column").insert(1,column_html)
index_html_file.write(str(html.prettify()))
index_html_file.close()


# """start parsing content in column.html"""
# filter_year_all =  column_html.find_all("div", class_= "filter-year")

# filter_author_path = Path("filter_author")
# filter_year_path = Path("filter_year")

# if not os.path.exists(filter_author_path):
#     os.makedirs(filter_author_path)
# if not os.path.exists(filter_year_path):
#     os.makedirs(filter_year_path)


for year in filter_years:
    base_html = open("./base.html", "r").read()
    html = BeautifulSoup(base_html, "html.parser")
    column_html = BeautifulSoup(open("./column.html", "r").read(),'html.parser')

    year_html_file = open(f"./{year}.html", "w")
    year_bibbase = f'<h2 style="margin-bottom:20px;">{year} Publications</h2> <script src={bibbase_url}&noBootstrap=1&jsonp=1&authorFirst=1&filter=year:{year}></script>'
    year_bibbase = BeautifulSoup(year_bibbase, features="lxml")
    html.find("div", class_= "index").insert(1,year_bibbase)
    html.find("div", class_= "secondary_column").insert(1,column_html)
    year_html_file.write(str(html.prettify()))
    year_html_file.close()

for author, value in filter_authors.items():
    base_html = open("./base.html", "r").read()
    html = BeautifulSoup(base_html, "html.parser")
    column_html = BeautifulSoup(open("./column.html", "r").read(),'html.parser')
      
    author_html_file = open(f"./{author}.html", "w")
    author_bibbase = f'<h2 style="margin-bottom:20px;">{author} Publications</h2> <script src={bibbase_url}&noBootstrap=1&jsonp=1&authorFirst=1&filter=authors:{value}></script>'
    author_bibbase = BeautifulSoup(author_bibbase, features="html.parser")


    html.find("div", class_= "index").insert(1,author_bibbase)
    html.find("div", class_= "secondary_column").insert(1,column_html)
    author_html_file.write(str(html.prettify()))
    author_html_file.close()



# webbrowser.open_new_tab("1.html")