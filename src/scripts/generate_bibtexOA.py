import pyalex
import bibtexparser
import json
import requests
import re
from pathlib import Path
from calendar import month_name

# Base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Paths for various directories
CONFIG_DIR = BASE_DIR / "src" / "config"
STATIC_DIR = BASE_DIR / "src" / "static"
LOGS_DIR = BASE_DIR / "src" / "logs"
TEMPLATES_DIR = BASE_DIR / "src" / "templates"
BIB_DIR = STATIC_DIR / "bib"
CSS_DIR = STATIC_DIR / "css"
JS_DIR = STATIC_DIR / "js"

VALID_PUBLICATION_TYPES = {'article'}


# Function to load authors from a JSON file
def load_authors():
    with open(CONFIG_DIR / "authors.json", "r", encoding="utf-8") as f:
        authors_json = json.load(f)    
    return authors_json

# Function to load publication data from current Bibtex file
def load_bibtex():
    with open(BIB_DIR / 'Publications.bib', "r", encoding="utf-8") as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)   
    return bib_database

# Function to get bibtex  
def get_bibtex(pub, author_id):

    # Load the DOI URL  
    url = pub['doi']
    headers = {"accept": "application/x-bibtex"}

    all_bibtex_types = ["article", "book", "booklet", 
                        "inbook", "conference", "incollection", 
                        "inproceedings", "manual", "mastersthesis",
                          "misc", "phdthesis",  "proceedings", 
                          "techreport", "unpublished"]
    print(f" >> Creating BibTeX for \"{pub['display_name']}\"...")

    if url:
        print(f" >> Downloading from url: \"{url}\"...")
        # Check if the BIBTEX is available for the DOI 
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            bib_entry = response.text
            pattern = re.search(r'\@(.*?)\{',bib_entry)
            if pattern:
                if pattern.group(1) in all_bibtex_types:
                    print(f" >> BibTeX downloaded for current publication (url:{url}, type: {pattern.group(1)}).")
                    bib_entry = bib_entry.replace("{", f"{{{author_id}:", 1)  # Format the id field to include the author_id
                    bib = bibtexparser.loads(bib_entry)
                    if len(bib.entries) != 0:
                        bib.entries[0]['url'] = url.replace("http:", "https:")  # Replace https with http in the URL
                        bibtex_string = bibtexparser.dumps(bib)
                        if bibtex_string or bibtex_string!="":
                            print(f" >> BibTeX API successfully read downloaded entry (url:{url}).")
                            return bibtex_string
                        else:
                            print(" >> BibTeX API returned an empty entry, creating custom BibTeX entry instead...")
                            pass
                    else:
                        print(" >> BibTeX API can't proccess entry, creating custom BibTeX entry instead...")
                        pass
                    
            else:
                print(" >> Formating error of DOI API response, creating custom BibTeX entry instead...")
                pass                                
        except requests.exceptions.RequestException as e:
            print(f" >> Error fetching BibTeX from DOI url: {e}")
            print(" >> Creating custom BibTeX entry instead...")
            pass
    else:
        print(f" >> DOI URL is empty, creating custom BibTeX entry instead...")

    try: 
        # Check if the publication has a primary location, a source and a display name
        if pub["primary_location"]:
            pub_url = pub["primary_location"]["landing_page_url"]
            if pub["primary_location"]["source"]:
                if "display_name" in pub["primary_location"]["source"]:
                    venue = pub["primary_location"]["source"]["display_name"]
                    print(f" >> Venue: {venue} (type: {pub['type']}).")
                else:
                    venue = ""
                    print(f" >> Venue unknown for current publication (type: {pub['type']}).")
            else:
                venue = ""
                print(f" >> Source unknown for current publication (type: {pub['type']}).")
        else:
            venue = ""
            pub_url = pub["id"]
            print(f" >> Primary location unknown for current publication (type: {pub['type']}).")


        # Create a custom BibTeX entry
        publication_entry = {
            'ENTRYTYPE': pub["type"].lower().replace("-", ""),
            'ID': f"{author_id}:{str(pub['id'])}",
            'title': str(pub["title"]),
            'year': str(pub["publication_year"]),
            'month': str(month_name[int(pub['publication_date'].split('-')[1])]),
            'journal': str(venue),
            'volume': str(pub["biblio"]["volume"]),
            'issue': str(pub["biblio"]["issue"]),
            'pages': str(pub["biblio"]["first_page"]) + "-" + str(pub["biblio"]["last_page"]),
            'url': str(pub_url),
            'doi': str(pub["doi"]),
            'author': " and ".join([author["author"]["display_name"] for author in pub["authorships"]]),
        }

        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = [publication_entry]
        return bibtexparser.dumps(db)
    except Exception as e: 
        # Handle any errors that occur during custom BibTeX entry creation
        print(f" >> Error creating custom BibTeX entry: {e}")
        print(f" >> Publication ID: {pub['id']}, Author ID: {author_id}, Display Name: {pub['display_name']}")
        print(f" >> Publication: {pub['primary_location']}")
        print(f" >> Publication: {pub}")
        print(" ")
        return ""



def update_publication_stats(publication_stats, publication_year, publication_type, author, valid=True):
    # Update the publication statistics
    publication_stats['total_number_of_publications'] += 1

    # Check if the type of the publication is already in the dictionary
    publication_stats['publications_per_type'].setdefault(publication_type,0)
    publication_stats['publications_per_type'][publication_type] += 1

    # Check if the publication is valid
    if valid:
        # Update valid publication statistics
        publication_stats['total_number_of_valid_publications'] += 1
        publication_stats['valid_publications_per_author'].setdefault(author, 0)
        publication_stats['valid_publications_per_author'][author] += 1
        publication_stats['valid_publications_per_year'].setdefault(publication_year, 0)
        publication_stats['valid_publications_per_year'][publication_year] += 1
    else:
        # Update skipped publication statistics
        publication_stats['total_number_of_skipped_publications'] += 1
        publication_stats['skipped_publications_per_author'].setdefault(author, 0)
        publication_stats['skipped_publications_per_author'][author] += 1 
        publication_stats['skipped_publications_per_year'].setdefault(publication_year, 0)
        publication_stats['skipped_publications_per_year'][publication_year] += 1

    return publication_stats

# Function to generate a BibTeX and statistics for a group of authors
def generate_bibtex_and_stats():

    # Load authors from the JSON file
    authors_json = load_authors()

    # Load the current BibTeX file
    bib_database = load_bibtex()

    # Creates a list with all valid DOI urls in the BibTeX file
    doi_list = [entry['doi'].lower() for entry in bib_database.entries if 'doi' in entry and entry['doi'] is not None and entry['doi'] != 'None']
    for index, item in enumerate(doi_list):
        if not item.startswith("http"):
            doi_list[index] = 'https://doi.org/'+doi_list[index]
        # print(f"DOI URL: {doi_list[index]}")
    
    # Creates a list with all valid publication urls in the BibTeX file   
    url_list = [entry['url'] for entry in bib_database.entries if 'url' in entry  and entry['url'] is not None and entry['url'] != '']

    print(" ")

    authors_ids = []
    # Print the authors and their IDs
    for author, id in authors_json.items():
        print(f"Author: {author}, ID: {id}")
        authors_ids.append(id)

    print(" ")    
    print(f"Loaded {len(authors_ids)} authors from the configuration file.")
    print(" ")  

    # Initialize variables
    new_publications = 0
    valid_bibtex_publications = ""
    skipped_bibtex_publications = ""
    publication_stats = {'total_number_of_publications': 0,
                         'total_number_of_valid_publications': 0,
                         'total_number_of_skipped_publications': 0,
                         'publications_per_type': {},
                         'valid_publications_per_author': {},
                         'skipped_publications_per_author': {},
                         'valid_publications_per_year': {},
                         'skipped_publications_per_year': {}
                         }
    
    # PyAlex configuration
    pyalex.config.email = "vas4d@virginia.edu"
    pyalex.config.max_retries = 0
    pyalex.config.retry_backoff_factor = 0.1
    pyalex.config.retry_http_codes = [429, 500, 503]


    for author, author_id in authors_json.items():

        print(" ")
        print(f"=== Fetching publications for author: {author} (orcid:{author_id}) ===")
        print(" ")

        # Fetch publications from OpenAlex
        publication_search = pyalex.Works().filter(author={"orcid":author_id}, is_paratext=False).paginate(per_page=200)
        
        for page in publication_search:
            if len(page) == 0:
                break
            for pub in page:
                if (pub["type"] not in VALID_PUBLICATION_TYPES) or ('ALL' in VALID_PUBLICATION_TYPES):
                    publication_stats = update_publication_stats(publication_stats, pub['publication_year'], pub['type'], author, valid=False)
                else:
                    publication_stats = update_publication_stats(publication_stats, pub['publication_year'], pub['type'],author, valid=True)
                    
                    # check if the publication DOI is already in the current BibTeX file and 
                    pub_url = pub["primary_location"]["landing_page_url"] if pub["primary_location"] else ""
                    pub_openalexid = pub["id"]

                    pub_doi = pub['doi'].lower() if pub['doi'] is not None else ""
                    if not pub_doi.startswith("http") and pub_doi != "":
                        pub_doi = 'https://doi.org/'+pub_doi
                    if pub_doi in doi_list or pub_doi in url_list or pub_url in url_list or pub_openalexid in url_list:
                        print(f" (!) Publication already exists! (DOI:'{pub['doi']}'/Open Alex ID:'{pub_openalexid}'/url:'{pub_url}')") 
                    else:
                        print(f" >> New publication found! (DOI:'{pub['doi']}'/Open Alex ID:'{pub_openalexid}'/url:'{pub_url}')")
                        valid_bibtex_publications += get_bibtex(pub, author_id)
                        new_publications += 1


    print(" ")
    print("=== Finished fetching publications ===")
    print(" ")
    print(f"Total number of new publications: {new_publications}")
    print(" ")
    return (valid_bibtex_publications,skipped_bibtex_publications,publication_stats)


# Main function
if __name__ == "__main__":
    
    # Generate BibTeX and statistics
    (valid_bibtex_publications,skipped_bibtex_publications,publication_stats) = generate_bibtex_and_stats()
    
    print("BibTeX entries generated successfully!")
    print(" ")
    print(f"Publication statitics:\n{json.dumps(publication_stats, indent=4)}")

    # Save BibTeX file
    with open(BIB_DIR / 'Publications.bib', 'a', encoding='utf-8') as bibtex_file:
        bibtex_file.write(valid_bibtex_publications)

    # Save skipped publications
    # with open(BIB_DIR / 'SkippedPublications.bib', 'w', encoding='utf-8') as bibtex_file:
    #     bibtex_file.write(skipped_bibtex_publications)

    # Save statistics
    with open(LOGS_DIR / 'PublicationStatistics.json', 'w', encoding='utf-8') as stats_file:
        json.dump(publication_stats, stats_file, indent=4)