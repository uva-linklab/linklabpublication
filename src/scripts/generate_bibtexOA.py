# -*- coding: utf-8 -*-
import pyalex
from bibtexparser import dumps
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from collections import defaultdict
import re
import json
from pathlib import Path

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
def load_authors(filename="authors.json"):
    with open(CONFIG_DIR / filename, "r", encoding="utf-8") as f:
        authors_json = json.load(f)
    authors_ids = []
    for author, id in authors_json.items():
        print(f"Author: {author}, ID: {id}")
        authors_ids.append(id)
    return authors_ids

def normalize_string(value):
    """Normalize a string for case-insensitive and special character insensitive comparison."""
    if not value:
        return ""
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', value)).strip().lower()

def create_bibtex_entry(work_data):
    entry = {
        'ENTRYTYPE': work_data['type'].lower().replace("-", ""),
        "ID": work_data["id"].split("/")[-1],
        "title": work_data["title"],
        "author": " and ".join([author["author"]["display_name"] for author in work_data["authorships"]]),
        "year": str(work_data["publication_year"])
    }
    for key, value in entry.items():
        if value is None:
            entry[key] = "Not available"

    if work_data["primary_location"] and work_data["primary_location"]["source"]:
      entry["journal"] = work_data["primary_location"]["source"]["display_name"]
    else:
      entry["journal"] = "Journal not available"

    if work_data["doi"]:
        entry["doi"] = work_data["doi"]
    else:
        entry["doi"] = "DOI not available"

    db = BibDatabase()
    db.entries = [entry]
    
    return dumps(db)

def openalex_to_bibtex(author_ids):

    all_publications = []
    publication_search = pyalex.Works().filter(author={"id": ("|".join(author_ids))}).paginate(per_page=200)
    
    for page in publication_search:
        if len(page) == 0:
            break
        for element in page:
            all_publications.append(element)

    valid_bibtex_publications = ""
    skipped_publications = ""
    print(f"Total publications found: {len(all_publications)}")
    print("Generating bibtex entries...")
    for pub in all_publications:
        if pub["type"] not in VALID_PUBLICATION_TYPES:
            skip_entry = create_bibtex_entry(pub)
            skipped_publications += skip_entry
            # print(f"Skipping invalid type: {pub["type"]} for publication {pub["title"]}")
        else:
            # Create BibTeX entry
            bibtex_entry = create_bibtex_entry(pub)
            valid_bibtex_publications += bibtex_entry
    print("BibTeX entries generated successfully.")

    return (valid_bibtex_publications, skipped_publications)


if __name__ == "__main__":
    # Load authors from the JSON file
    author_ids = load_authors("authorsOA.json")

    (valid_bibtex_publications, skipped_publications) = openalex_to_bibtex(author_ids)

    # Save BibTeX file
    with open(BIB_DIR / 'Publications.bib', 'w', encoding='utf-8') as bibtex_file:
        bibtex_file.write(valid_bibtex_publications)

    # Save skipped publications
    with open(BIB_DIR  / 'SkippedPublications.bib', 'w', encoding='utf-8') as bibtex_file:
        bibtex_file.write(skipped_publications)


