from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
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

def load_base_html():
    base_html = open("./base.html", "r").read()
    html = BeautifulSoup(base_html, "html.parser")
    column_html = BeautifulSoup(open("./column.html", "r").read(),'html.parser')
    return html, column_html
# 
def get_bibbase_html(bibbase_url, filter_cond): # "year:2023"
    response = requests.get(f'{bibbase_url}&noBootstrap=1&authorFirst=1&filter={filter_cond}')
    r_html = response.text # get the response text. in this case it is HTML
    soup = BeautifulSoup(r_html, "html.parser") # parse the HTML
    body = soup.find('body')
    
    return body
# 
def create_and_init_html_file(filter):
    filter_html_file = open(f"./{filter}.html", "w")
    filter_bibbase = f'<h2 style="margin-bottom:20px;">{filter} Publications</h2> <div> </div>'
    filter_bibbase = BeautifulSoup(filter_bibbase, features="lxml")

    return filter_html_file, filter_bibbase


# Part 1/3: generate index.html !!
index_html_file = open("index.html", "w")
index_bibbase = f'<h2 style="margin-bottom:20px;">2023 Publications</h2> <div></div>'
index_bibbase = BeautifulSoup(index_bibbase, features="lxml")
bibbase_body = get_bibbase_html(bibbase_url, "year:2023")
tag = index_bibbase.div
tag.append(bibbase_body)

html, column_html = load_base_html()

html.find("div", class_= "index").insert(1,index_bibbase)
html.find("div", class_= "secondary_column").insert(1,column_html)
index_html_file.write(str(html.prettify()))
index_html_file.close()


# filter_author_path = Path("filter_author")
# filter_year_path = Path("filter_year")

# if not os.path.exists(filter_author_path):
#     os.makedirs(filter_author_path)
# if not os.path.exists(filter_year_path):
#     os.makedirs(filter_year_path)

# Part 2/3: create year.html !!
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

# Part 3/3: create faculty.html !!
print("generating faculty_htmls_file")
for author, value in tqdm(filter_authors.items()):
    html, column_html = load_base_html()
    author_html_file, author_bibbase = create_and_init_html_file(author)
      
    bibbase_body = get_bibbase_html(bibbase_url, f"authors:{value}")
    if bibbase_body is None:
        bibbase_body = '<span></span>'
    tag = author_bibbase.div
    tag.append(bibbase_body)

    html.find("div", class_= "index").insert(1,author_bibbase)
    html.find("div", class_= "secondary_column").insert(1,column_html)
    author_html_file.write(str(html.prettify()))
    author_html_file.close()

# webbrowser.open_new_tab("1.html")