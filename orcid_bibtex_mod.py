import requests
import json
import bibtexparser

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

ORCID_RECORD_API = "https://pub.orcid.org/v3.0"

def create_bibtex(id,title,year,month,journal,url,name,orcid):
    entry = {
        'ENTRYTYPE': 'article',
        'ID': orcid + ":" + id,
        'title': title,
        'year': year,
        'month': month,
        'journal': journal,
        'url': url,
        'author': name,
    }
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = [entry]
    return bibtexparser.dumps(db)

def safe_get(d, *keys, default=None):
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key)
        if d is None:
            return default
    return d

all_bibtex_publications = ""
publication_count = 0

# Iterates over every author, creates an author object and retrieves the publications list for a given author
for name, orcid in author_ids.items():
    response = requests.get(url=requests.utils.requote_uri(ORCID_RECORD_API + "/" + orcid),
    headers={'Accept': 'application/json'})
    response.raise_for_status()
    result = response.json()
    with open('data.json', 'a') as f:
            json.dump(result, f)
    works = result["activities-summary"]["works"]

    for group in works['group']:
        author_list = ""
        summary = group['work-summary']
        pub = summary[0]

        id = str(pub.get("put-code", ""))
        title = safe_get(pub, 'title', 'title', 'value', default="No Title")
        year = str(safe_get(pub, 'publication-date', 'year', 'value', default="Unknown Year"))
        month = safe_get(pub, 'publication-date', 'month', 'value', default="Unknown Month")
        journal = safe_get(pub, 'journal-title', 'value', default="Unknown Journal")
        url = safe_get(pub, 'url', 'value', default="No URL")

        path_to_publication = str(pub.get("path", ""))
        full_publication = requests.get(url=requests.utils.requote_uri(ORCID_RECORD_API + path_to_publication),headers={'Accept': 'application/json'})
        full_publication.raise_for_status()
        full_publication_data = full_publication.json()
        contributors = full_publication_data["contributors"]

        if(contributors is not None):
            for contributor in contributors['contributor']:
                contributor_name = contributor["credit-name"]["value"]
                author_list += (contributor_name + ", ")

        # Remove the last comma from the list of authors
        author_list = author_list[0:(len(author_list) - 2)]

        bibtex = create_bibtex(id,title,year,month,journal,url,author_list,orcid)
        all_bibtex_publications += bibtex
        publication_count += 1


with open('Link_Lab_Publications.bib', 'w') as bibtex_file:
    bibtex_file.write(all_bibtex_publications)
print("Processed " + str(publication_count) + " publications")