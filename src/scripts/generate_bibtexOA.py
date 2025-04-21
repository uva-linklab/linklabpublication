import pyalex
import bibtexparser
import json
import requests
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
        authors_ids = []
    for author, id in authors_json.items():
        print(f"Author: {author}, ID: {id}")
        authors_ids.append(id)
    return authors_ids

# Function to get bibtex  
def get_bibtex(pub, author_id):

    # Load the DOI URL  
    url = pub['doi']
    headers = {"accept": "application/x-bibtex"}

    # Check if the BIBTEX is available for the DOI
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        bib_entry = response.text
        return bib_entry.replace("{ ", f"{{ {author_id}:", 1)  # Format the id field to include the author_id
    except requests.exceptions.RequestException as e:
        print(f"Error fetching BibTeX from DOI url: {e}")
        print("Creating custom BibTeX entry instead.")
        pass

    try:
        pub_id = str(pub["id"])
        # Create a custom BibTeX entry
        publication_entry = {
            'ENTRYTYPE': pub["type"].lower().replace("-", ""),
            'ID': f"{author_id}:{pub_id}",
            'title': str(pub["title"]),
            'year': str(pub["publication_year"]),
            'month': str(month_name[int(pub['publication_date'].split('-')[1])]),
            'journal': str(pub["primary_location"]["display_name"]),
            'volume': str(pub["biblio"]["volume"]),
            'issue': str(pub["biblio"]["issue"]),
            'pages': str(pub["biblio"]["first_page"]) + "-" + str(pub["biblio"]["last_page"]),
            'url': str(pub["primary_location"]["landing_page_url"]),
            'doi': str(pub["doi"]),
            'author': " and ".join([author["author"]["display_name"] for author in pub["authorships"]]),
        }

        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = [publication_entry]
        return bibtexparser.dumps(db)
    except Exception as e:  
        print(f"Error creating custom BibTeX entry: {e}")
        print(f"Publication ID: {pub['id']}, Author ID: {author_id}, Display Name: {pub['display_name']}")
        return ""



def update_publication_stats(publication_stats, publication_year, publication_type, author_id, valid=True):
    # Update the publication statistics
    publication_stats['total_number_of_publications'] += 1

    # Check if the type of the publication is already in the dictionary
    publication_stats['publications_per_type'].setdefault(publication_type,0)
    publication_stats['publications_per_type'][publication_type] += 1

    # Check if the publication is valid
    if valid:
        # Update valid publication statistics
        publication_stats['total_number_of_valid_publications'] += 1
        publication_stats['valid_publications_per_author'].setdefault(author_id, 0)
        publication_stats['valid_publications_per_author'][author_id] += 1
        publication_stats['valid_publications_per_year'].setdefault(publication_year, 0)
        publication_stats['valid_publications_per_year'][publication_year] += 1
    else:
        # Update skipped publication statistics
        publication_stats['total_number_of_skipped_publications'] += 1
        publication_stats['skipped_publications_per_author'].setdefault(author_id, 0)
        publication_stats['skipped_publications_per_author'][author_id] += 1 
        publication_stats['skipped_publications_per_year'].setdefault(publication_year, 0)
        publication_stats['skipped_publications_per_year'][publication_year] += 1

    return publication_stats

# Function to generate a BibTeX and statistics for a group of authors
def generate_bibtex_and_stats():

    # Load authors from the JSON file
    author_ids = load_authors()
    print(f"Loaded {len(author_ids)} authors from the configuration file.")

    # Initialize variables
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

    for author_id in author_ids:
        print(f"Fetching publications for author ID: {author_id}")

        # Fetch publications from OpenAlex
        publication_search = pyalex.Works().filter(author={"orcid":author_id}).paginate(per_page=200)
        
        for page in publication_search:
            if len(page) == 0:
                break
            for pub in page:
                if (pub["type"] not in VALID_PUBLICATION_TYPES) or ('ALL' in VALID_PUBLICATION_TYPES):
                    publication_stats = update_publication_stats(publication_stats, pub['publication_year'], pub['type'], author_id, valid=False)
                    skipped_bibtex_publications += get_bibtex(pub, author_id)
                else:
                    publication_stats = update_publication_stats(publication_stats, pub['publication_year'], pub['type'],author_id, valid=True)
                    valid_bibtex_publications += get_bibtex(pub, author_id)

    return (valid_bibtex_publications,skipped_bibtex_publications,publication_stats)


# IF this script is run directly, execute the main function
if __name__ == "__main__":
    
    # Generate BibTeX and statistics
    (valid_bibtex_publications,skipped_bibtex_publications,publication_stats) = generate_bibtex_and_stats()
    
    print("BibTeX entries generated successfully!")
    print(" ")
    print(f"Publication statitics:\n{json.dumps(publication_stats, indent=4)}")

    # Save BibTeX file
    with open(BIB_DIR / 'Publications.bib', 'w', encoding='utf-8') as bibtex_file:
        bibtex_file.write(valid_bibtex_publications)

    # Save skipped publications
    with open(LOGS_DIR / 'SkippedPublications.bib', 'w', encoding='utf-8') as bibtex_file:
        bibtex_file.write(skipped_bibtex_publications)

    # Save statistics
    with open(LOGS_DIR / 'PublicationStatistics.json', 'w', encoding='utf-8') as stats_file:
        json.dump(publication_stats, stats_file, indent=4)