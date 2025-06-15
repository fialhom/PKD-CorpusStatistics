##### IMPORTS #####

from bs4 import BeautifulSoup as bs
import os
import pandas as pd
import json

# Metadata CSV
meta = pd.read_csv("meta_files/metadata.csv")

# I saved all the stories as a JSON when I first made them txt files, so I just parsed this because it was simple logic

with open('meta_files/all_stories.json', 'r') as file:
    stories = json.load(file)
    
meta_stories = {}

# Make DICT with text and metadata from CSV
for title, story in stories.items():
    for index, row in meta.iterrows():
        if row['Title'].lower() == title.lower():
            row_dict = row.to_dict()
            row_dict['TEXT'] = story
            meta_stories[title] = row_dict
data = []
for story in meta_stories:
    data.append(meta_stories[story])       

print("\nConverting texts...", flush=True)
# Convert every entry in DICT into TEI, output as tei file
count = 1
for story in data:
    chaps = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV"]
    title = story['Title']
    collection = story['Source']
    if collection[:13] == "The Collected":
        publisher = "Citadel Twilight"
    else:
        publisher = ""
        collection = "" 
    writDate = story['Year Written']
    pubDate = story['Year Published']
    author = story['Author']
    notes = story['Notes']
    
    print(f"[{count}/118]\t{story['File']} ... ", end='', flush=True)
    # TEI Header
    tei_header = f"""
        <teiHeader>
            <fileDesc>
            <seriesStmt>
                <title>{collection}</title>
            </seriesStmt>
            <titleStmt>
                <title>{title}</title>
                <author>{author}</author>
            </titleStmt>
            <publicationStmt>
                <pubPlace>United States</pubPlace>
                <publisher>{publisher}</publisher>
                <date>{pubDate}</date>
            </publicationStmt>
            <notesStmt>
                <note>{notes}</note>
            </notesStmt>
            <sourceDesc>
                <bibl>
                    <date>{writDate}</date>
                </bibl>
            </sourceDesc>
            </fileDesc>
            <profileDesc>
            <langUsage>
                <language>eng</language>
            </langUsage>
            </profileDesc>
        </teiHeader>"""
    
    # TEI Body
    tei_body = "<body>"
    in_div = False
    chaptered = False
    for line in story['TEXT']:
        if line in chaps:
            chaptered = True
            if in_div is True:
                tei_body += "</div>\n"
            line_str = f"<div>\n<head>{line}</head>\n"
            in_div = True
            tei_body += line_str
        else:
            line_str = f"<p>{line}</p>\n"
            tei_body += line_str
    if chaptered == True:
        tei_body += "</div>\n</body>\n"
    else:
        tei_body += "</body>\n"
    tei = f"<?xml version='1.0' encoding='UTF-8'?>\n<TEI>{tei_header}{tei_body}\n</TEI>"
    
    # Soup
    soup = bs(tei, "xml")
    file = title.lower().replace(" ", "_").replace("'", "").replace(".","").replace("?", "").replace("!", "").replace(":", "").replace(",", "")
    filename = f"tei_files/{file}.tei"
    
    # Output files
    try:
        os.mkdir("tei_files")
        with open(filename, "w", encoding="utf-8") as o:
            o.write(soup.prettify())
        print("TEI\n")
    except FileExistsError:
        with open(filename, "w", encoding="utf-8") as o:
            o.write(soup.prettify())
        print("!")
    count+=1
    
    
print("done.")