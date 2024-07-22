from scholarly import scholarly,ProxyGenerator
import bibtexparser
from datetime import datetime
import json

#Proxy so that google scholar will not block your IP for too many requests. Uncomment if you run into issues with this. Using the proxy causes retrieval to take MUCH longer.
pg = ProxyGenerator()
pg.FreeProxies()
scholarly.use_proxy(pg)

# List of Link Lab authors. Values are ORCID [0] and google scholar id [1]
author_ids = {
    # "Negin Alemazkoor": ["0000-0003-0221-3985","lDDZYr0AAAAJ"],
    # "Homa Alemzadeh": ["0000-0001-5279-842X","sXpmLxUAAAAJ"], 
    # "Lawrence E. Band": [ "0000-0003-0461-0503","hKmmMrAAAAAJ"],
    # "Laura E. Barnes": ["0000-0001-8224-5164","h-Lr0bQAAAAJ"],
    # "Madhur Behl": ["0000-0002-5921-0331", "bj_imaYAAAAJ"],
    # "Nicola Bezzo": ["0000-0001-6627-5048","lyNOlzoAAAAJ"], 
    # "Matthew Bolton": ["0000-0002-3649-5637","6c19RG8AAAAJ"],
    # "Steven Bowers": ["0000-0002-4243-8663","0h-RyocAAAAJ"],
    # "Maite Brandt-Pearce": ["0000-0002-2566-8280","KFLFbWoAAAAJ"], 
    # "Benton H. Calhoun": ["0000-0002-3770-5050","I7a8pr0AAAAJ"], 
    # "Brad Campbell": ["0000-0002-4103-8107","MLx5TCQAAAAJ"], 
    # "Qing Chang": ["0000-0003-3744-1371","TfPemJcAAAAJ"],
    # "Donna T. Chen": ["0000-0002-7026-3418","l20iH34AAAAJ"],
    # "Seokhyun Chung": ["0000-0001-5176-4180","4hYcwMEAAAAJ"],
    # "Haibo Dong": ["0000-0001-7823-7014","SrYdog8AAAAJ"],
    # "Afsaneh Doryab": ["0000-0003-1575-385X","O0lONMkAAAAJ"],
    # "Lu Feng": ["0000-0002-4651-8441", "HiyMQzEAAAAJ"],
    # "Tomonari Furukawa": ["0000-0003-2811-4221","VwpBvvgAAAAJ"],
    # "Gregory J. Gerling": ["0000-0003-3137-3822","ibBUGLAAAAAJ"],
    # "Jonathan L. Goodall": ["0000-0002-1112-4522","M9aKXDwAAAAJ"],
    # "Devin K. Harris": ["0000-0003-0086-1073","Y0e7hZsAAAAJ"],
    # "Seongkook Heo": ["0000-0003-2004-4812","7r0_F0kAAAAJ"],
    # "Arsalan Heydarian": ["0000-0001-5972-6947", "VTdMErEAAAAJ"],
    # "Tariq Iqbal": ["0000-0003-0133-1234","t_ndTI4AAAAJ"],   
    # "Yen-Ling Kuo": ["0000-0002-6433-6713","pNkyRs4AAAAJ"],
    "Venkataraman Lakshmi": ["0000-0001-7431-9004","vbNdSy0AAAAJ"], 
    # "James H. Lambert": ["0000-0002-0697-8339","qVfffxkAAAAJ"], 
    # "Zongli Lin": ["0000-0003-1589-1443","n4fG76YAAAAJ"], 
    # "Felix Xiaozhu Lin": ["0000-0002-1615-6419","f6FFhS8AAAAJ"],
    # "zhen Liu": ["0000-0001-8013-3804","JBKiFFQAAAAJ"], 
    # "Eric Loth": ["0000-0003-4113-733X","AqEcQtYAAAAJ"],
    # "Osman E. Ozbulut": ["0000-0003-3836-3416","VdoAeqAAAAAJ"], 
    # "Byungkyu Brian Park": ["0000-0003-4597-6368","I23GOcEAAAAJ"],
    # "Daniel Quinn": ["0000-0002-5835-5221","8A8eaZMAAAAJ"],
    # "Sara L. Riggs": ["0000-0002-0112-9469","ALjgMAoAAAAJ"],
    # "Haiying Shen": ["0000-0002-7548-6223","W0Cx7ZAAAAAJ"],
    # "Cong Shen": ["0000-0002-3148-4453","70LBhKcAAAAJ"],
    # "Brian Smith": ["0000-0001-5102-6399","9uFvl5wAAAAJ"],
    # "Mircea R. Stan": ["0000-0003-0577-9976","5DLZvlMAAAAJ"],
    # "Yixin Sun": ["0000-0001-6650-4373","ov72AA4AAAAJ"],
    # "Ye Sun": ["0000-0003-1086-8017","7oNkNtIAAAAJ"],
}

# This function takes in a scholarly publication object and creates and bibtex object out of it then returns it.
def create_bibtex(pub):
    bib_data = pub.get('bib', {})
    entry = {
        'ENTRYTYPE': 'article',
        'ID': pub.get('author_pub_id', 'Unknown'),
        'title': bib_data.get('title', 'Unknown Title'),
        'author': bib_data.get('author', 'Unknown Author'),
        'year': str(bib_data.get('pub_year', '')),
        'journal': bib_data.get('journal', 'Unknown journal'),
        'URL': pub.get('pub_url', ''),
    }
    
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = [entry]
    return bibtexparser.dumps(db)

# Iterates over every author, creates an author object and retrieves the publications list for a given author
for name, (orcid, scholar_id) in author_ids.items():
    filled_author = {}
    try:
        # Get the author object for a given person and fill it with information from google scholar 
        author = scholarly.search_author_id(scholar_id)
        filled_author = scholarly.fill(author,sections=["publications"])

        # Get the publications list, and the recent publications
        publications = filled_author['publications']
        selected_publications = publications[492:805]
        recent_publications = [pub for pub in publications if int(pub.get('bib', {}).get('pub_year', 0)) >= datetime.now().year]
        print("Processing " + name + " " + author.get('scholar_id'))


        # Iterates over every publication for an author, fill with the relevant information, writes it to the bib file
        for pub in selected_publications: 
            try:
                scholarly.fill(pub)
                bibtex = create_bibtex(pub)
                print(f"Processed: {pub['bib'].get('title', 'Unknown Title')}")
                print(bibtex)
                with open('test.bib', 'a') as bibtex_file:
                    bibtex_file.write(bibtex)

            except Exception as e:
                print(f"Error processing publication: {str(e)}")

    except Exception as e:
        print(f"Error for {name}: {str(e)}")
