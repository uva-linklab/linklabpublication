import requests
import json
import bibtexparser
from tqdm import tqdm  # For progress bar
from collections import defaultdict
import re
from pathlib import Path

# Function to load authors from a JSON file
def load_authors():
    with open(Path(__file__).parent / "authors.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Load authors from the JSON file
author_ids = load_authors()

ORCID_RECORD_API = "https://pub.orcid.org/v3.0"

def create_bibtex(id, title, year, month, journal, volume, url, authors, doi, orcid, pub_type):
    entry = {
        'ENTRYTYPE': pub_type.lower().replace("-", ""),
        'ID': f"{orcid}:{id}",
        'title': title,
        'year': year,
        'month': month,
        'journal': journal,
        'volume': volume,
        'url': url,
        'doi': doi,
        'author': authors,
    }
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = [entry]
    return bibtexparser.dumps(db)

def safe_get(d, *keys):
    for key in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(key)
        if d is None:
            return None
    return d

def normalize_string(value):
    """Normalize a string for case-insensitive and special character insensitive comparison."""
    if not value:
        return ""
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', value)).strip().lower()

all_bibtex_publications = ""
all_publications_json = []
skipped_publications = []
publication_count = 0

VALID_PUBLICATION_TYPES = {'journal-article', 'conference-paper', 'book-chapter', 'book'}

# Statistics dictionaries
publications_per_author = defaultdict(int)
publications_per_year = defaultdict(int)
publications_per_type = defaultdict(int)

for name, orcid in tqdm(author_ids.items(), desc="Processing Authors"):
    try:
        print(f"Fetching data for {name} (ORCID: {orcid})")
        response = requests.get(
            url=f"{ORCID_RECORD_API}/{orcid}",
            headers={'Accept': 'application/json'}
        )
        response.raise_for_status()
        result = response.json()

        works = safe_get(result, "activities-summary", "works", "group") or []
        print(f"Found {len(works)} works for {name}")
        for work in works:
            summaries = work.get("work-summary", [])
            for pub in summaries:
                pub_id = str(pub.get("put-code", ""))
                title = safe_get(pub, "title", "title", "value")
                if not title:
                    print(f"Skipping publication without title (ID: {pub_id})")
                    continue

                year = safe_get(pub, "publication-date", "year", "value")
                month = safe_get(pub, "publication-date", "month", "value")
                journal = safe_get(pub, "journal-title", "value")
                url = safe_get(pub, "url", "value")
                volume = safe_get(pub, "volume", "value")
                doi = None
                external_ids = safe_get(pub, "external-ids", "external-id") or []
                for eid in external_ids:
                    if eid.get("external-id-type") == "doi":
                        doi = eid.get("external-id-value")

                pub_type = safe_get(pub, "type")

                if pub_type not in VALID_PUBLICATION_TYPES:
                    skip_entry = {
                        "id": pub_id,
                        "title": title,
                        "type": pub_type,
                        "author": name,
                        "orcid": orcid,
                    }
                    skipped_publications.append(skip_entry)
                    print(f"Skipping invalid type: {pub_type} for publication {title}")
                    continue

                print(f"Processing publication: {title} (ID: {pub_id}, Type: {pub_type})")

                # Fetch full publication details for contributors
                full_pub_response = requests.get(
                    url=f"{ORCID_RECORD_API}/{orcid}/work/{pub_id}",
                    headers={'Accept': 'application/json'}
                )
                full_pub_response.raise_for_status()
                full_pub_data = full_pub_response.json()

                authors = []
                contributors = safe_get(full_pub_data, "contributors", "contributor") or []
                for contributor in contributors:
                    credit_name = safe_get(contributor, "credit-name", "value")
                    if credit_name:
                        authors.append(credit_name)

                authors_str = ", ".join(authors)

                # Create BibTeX entry
                bibtex = create_bibtex(pub_id, title, year, month or "", journal or "", volume or "", url or "", authors_str, doi or "", orcid, pub_type)
                all_bibtex_publications += bibtex

                # Create JSON entry
                publication_entry = {
                    "id": pub_id,
                    "title": title,
                    "year": year,
                    "month": month,
                    "journal": journal,
                    "volume": volume,
                    "url": url,
                    "doi": doi,
                    "type": pub_type,
                    "authors": authors,
                    "orcid": orcid,
                    "author_name": name,
                }
                all_publications_json.append(publication_entry)
                publication_count += 1

                # Update statistics
                publications_per_author[name] += 1
                if year:
                    publications_per_year[year] += 1
                publications_per_type[pub_type] += 1

    except Exception as e:
        print(f"Error processing {name} ({orcid}): {e}")

with open('Publications.bib', 'w', encoding='utf-8') as bibtex_file:
    bibtex_file.write(all_bibtex_publications)

# with open('Publications.json', 'w', encoding='utf-8') as json_file:
#     json.dump(all_publications_json, json_file, indent=4)

# with open('SkippedPublications.log', 'w', encoding='utf-8') as log_file:
#     for skipped in skipped_publications:
#         log_file.write(json.dumps(skipped) + '\n')

# # Save statistics
# with open('PublicationStatistics.json', 'w', encoding='utf-8') as stats_file:
#     stats = {
#         "publications_per_author": publications_per_author,
#         "publications_per_year": publications_per_year,
#         "publications_per_type": publications_per_type,
#         "total_publications": publication_count,
#         "total_skipped": len(skipped_publications),
#     }
#     json.dump(stats, stats_file, indent=4)

# print(f"Processed {publication_count} valid publications in total.")
# print(f"Skipped {len(skipped_publications)} invalid publications. Check 'SkippedPublications.log'.")
# print(f"Statistics saved in 'PublicationStatistics.json'.")
