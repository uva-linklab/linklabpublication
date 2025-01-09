from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
import requests
import json
import re

#------------------------------------------------------------------

# Load authors from a JSON file
def load_authors():
    # with open(Path(__file__).parent / "authors.json", "r", encoding="utf-8") as f:
    with open(Path(__file__).parent.parent / "authors.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Parse BibBase file to extract publication years and pagination info
def parse_bibbase(bibbase_url):
    response = requests.get(bibbase_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch BibBase file.")

    bib_content = response.text
    years = set()
    publications = []
    
    # Parse BibTeX entries
    entries = re.findall(r"@article\{.*?\}", bib_content, re.DOTALL)
    for entry in entries:
        # Extract publication metadata
        year_match = re.search(r"year\s*=\s*\{(\d{4})\}", entry)
        author_match = re.search(r"author\s*=\s*\{(.*?)\}", entry, re.DOTALL)
        title_match = re.search(r"title\s*=\s*\{(.*?)\}", entry)
        doi_match = re.search(r"doi\s*=\s*\{(.*?)\}", entry)
        url_match = re.search(r"url\s*=\s*\{(.*?)\}", entry)
        journal_match = re.search(r"journal\s*=\s*\{(.*?)\}", entry)
        month_match = re.search(r"month\s*=\s*\{(.*?)\}", entry)

        # Add year to set
        if year_match:
            years.add(year_match.group(1))
        
        # Create publication object
        if year_match and title_match:
            publication = {
                "year": year_match.group(1),
                "authors": [a.strip() for a in author_match.group(1).split(",")] if author_match else [],
                "title": title_match.group(1),
                "doi": doi_match.group(1) if doi_match else None,
                "url": url_match.group(1) if url_match else None,
                "journal": journal_match.group(1) if journal_match else "Unknown",
                "month": month_match.group(1) if month_match else None,
            }
            publications.append(publication)
    
    return sorted(years, reverse=True), publications

# Load authors and parse BibBase
author_ids = load_authors()
bibbase_url = "https://bibbase.org/show?bib=https://bibbase.org/f/d83cfSGB7mDcZZ8au/Small_Link_Lab_Publications.bib"
filter_years, publications = parse_bibbase(bibbase_url)

#------------------------------------------------------------------

# Generate base HTML
def load_base_html():
    base_html = open("./base.html", "r", encoding="utf-8").read()
    html = BeautifulSoup(base_html, "html.parser")
    return html

# Create and initialize HTML file
def create_and_init_html_file(file_name, title):
    html = load_base_html()
    main_content = html.find("main")
    main_content.clear()

    # Add title and publication container
    main_content.append(html.new_tag("h2", string=title, attrs={"class": "page-title"}))
    publications_div = html.new_tag("div", id="publications", attrs={"class": "publication-container"})
    main_content.append(publications_div)

    return html, publications_div

# Generate HTML with publications and filters
def generate_html(output_file, title, filtered_publications):
    html, publications_div = create_and_init_html_file(output_file, title)

    # Add publications
    for pub in filtered_publications:
        card = html.new_tag("div", attrs={"class": "publication-card", "data-year": pub["year"], "data-authors": ",".join(pub["authors"])})
        card.append(html.new_tag("h3", string=pub["title"]))
        card.append(html.new_tag("p", string=f"Authors: {', '.join(pub['authors'])}"))
        card.append(html.new_tag("p", string=f"Year: {pub['year']}"))
        card.append(html.new_tag("p", string=f"Journal: {pub['journal']}"))
        if pub["doi"]:
            doi_link = html.new_tag("a", href=f"https://doi.org/{pub['doi']}", string="DOI", target="_blank")
            card.append(doi_link)
        if pub["url"]:
            url_link = html.new_tag("a", href=pub["url"], string="Read More", target="_blank")
            card.append(url_link)
        publications_div.append(card)

    # Add filters dynamically
    filter_container = html.new_tag("div", attrs={"class": "filters"})
    
    # Year filter
    year_filter = html.new_tag("select", id="yearFilter", multiple=True)
    for year in filter_years:
        option = html.new_tag("option", value=year, string=year)
        year_filter.append(option)
    filter_container.append(year_filter)

    # Author filter
    author_filter = html.new_tag("select", id="authorFilter", multiple=True)
    for author in author_ids.keys():
        option = html.new_tag("option", value=author, string=author)
        author_filter.append(option)
    filter_container.append(author_filter)

    # Type filter
    type_filter = html.new_tag("select", id="typeFilter")
    type_filter.append(html.new_tag("option", value="", string="All Types"))
    type_filter.append(html.new_tag("option", value="article", string="Article"))
    type_filter.append(html.new_tag("option", value="conference-paper", string="Conference Paper"))
    filter_container.append(type_filter)

    # Keyword filter
    keyword_filter = html.new_tag("input", id="keywordFilter", type="text", placeholder="Search by keywords")
    filter_container.append(keyword_filter)

    # Apply button
    apply_button = html.new_tag("button", id="applyFilters", string="Apply Filters")
    filter_container.append(apply_button)

    html.find("nav").append(filter_container)

    # Save HTML
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(str(html.prettify()))

#------------------------------------------------------------------

# Generate index.html
print("Generating index.html")
generate_html("index.html", "Link Lab Publications", publications)

# Generate year-based HTML files
print("Generating year-based HTML files")
for year in tqdm(filter_years):
    year_pubs = [pub for pub in publications if pub["year"] == year]
    generate_html(f"{year}.html", f"Publications for {year}", year_pubs)

# Generate author-based HTML files
print("Generating author-based HTML files")
for author in tqdm(author_ids.keys()):
    author_pubs = [pub for pub in publications if author in pub["authors"]]
    generate_html(f"{author}.html", f"Publications by {author}", author_pubs)
