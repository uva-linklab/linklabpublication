# -*- coding: utf-8 -*-
import requests
import json
import bibtexparser
from tqdm import tqdm  # For progress bar
from collections import defaultdict
import re

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
    'Rohan Chandra': '0000-0003-4843-6375',
}

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

# Global seen publication sets
seen_publications_global = set()
seen_skipped_publications = set()

# Statistics dictionaries
publications_per_author = defaultdict(int)
publications_per_year = defaultdict(int)
publications_per_type = defaultdict(int)

for name, orcid in tqdm(author_ids.items(), desc="Processing Authors"):
    seen_publications = set()  # Keep track of publications seen for this author
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
                
                # Create normalized key for deduplication
                normalized_title = normalize_string(title)
                global_key = f"{normalized_title}:{orcid}"

                if global_key in seen_publications_global:
                    print(f"Skipping duplicate publication globally: {title} for {name}")
                    continue

                seen_publications_global.add(global_key)

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
                    if global_key not in seen_skipped_publications:
                        seen_skipped_publications.add(global_key)
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

with open('Publications.json', 'w', encoding='utf-8') as json_file:
    json.dump(all_publications_json, json_file, indent=4)

with open('SkippedPublications.log', 'w', encoding='utf-8') as log_file:
    for skipped in skipped_publications:
        log_file.write(json.dumps(skipped) + '\n')

# Save statistics
with open('PublicationStatistics.json', 'w', encoding='utf-8') as stats_file:
    stats = {
        "publications_per_author": publications_per_author,
        "publications_per_year": publications_per_year,
        "publications_per_type": publications_per_type,
        "total_publications": publication_count,
        "total_skipped": len(skipped_publications),
    }
    json.dump(stats, stats_file, indent=4)

print(f"Processed {publication_count} valid publications (journals, conferences, book-chapters) in total.")
print(f"Skipped {len(skipped_publications)} invalid or unsupported publications. Check 'SkippedPublications.log'.")
print(f"Statistics saved in 'PublicationStatistics.json'.")
