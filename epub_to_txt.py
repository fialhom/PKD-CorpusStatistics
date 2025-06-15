"""I generated the metadata and text files programatically, and this was the code I used to do so. The source files were epubs of the collections, a few text files, and a csv of titles and years with notes, scraped from wikipedia and the notes from each respective volume"""

##### IMPORTS #####

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup as bs
import os
import pandas as pd
import json
import warnings

# There's a future/user warning I don't like to see
warnings.filterwarnings("ignore", category=FutureWarning, module="ebooklib")
warnings.filterwarnings("ignore", category=UserWarning, module="ebooklib")

##### RAW DATA #####

# Gets all my epub collections from the short stories folder
folder = 'source_files/short_stories'
files = os.listdir(folder)
epub_files = [os.path.join(folder, file) for file in files if file.endswith('.epub')]

# Three stories were missing from Collection 3 in every version I could find; I downloaded epubs for each individually, then converted to TXT using Calibre. I then imported them here to get rid of the apostrophes and make them the same format as the rest.
text_files = [os.path.join(folder, file) for file in files if file.endswith('.txt')]
print("READ: Epub and txt data")

##### DATA HANDLING #####

## Final Dictionary will be a full title as the key; each value will be a list of strings, with each string being a paragraph or subheading in the story.
#### short_stories = {'title': ['head_0, 'par_1', 'par_2']}

# Make dict of all text file stories
texts = {}
for file in text_files:
    with open(file, 'r', encoding="utf-8") as k:
        title = k.readline().replace("\n", "")
        titlef = title.lower().replace(" ", "_")
        tempfile = k.readlines()
    modfile = []
    for line in tempfile:
        form = line.replace('“', '"').replace('”', '"').replace("’", "'").replace("‘", "'").replace("\n", "").replace("—", "--") # Get rid of anything fancy and convert to plaintext
        if not form:
            continue
        else:
            modfile.append(form)
    texts[title] = modfile

# Makes dict of every story item in collection as entry in EPUB dictionary
epubs = {}
for epubfile in epub_files:
    book = epub.read_epub(epubfile) # Read in epub
    title = book.get_metadata('DC', 'title') # Gets epub title
    title = title[0][0]
    bodies = ""
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT: 
            bodies += f"{item.get_body_content().decode('utf-8')}" # Concat because stories stretched over multiple html files
    soup = bs(bodies, 'lxml') # Makes soup of all the <bodies>
    stories = soup.find_all('h1') # Each story has a heading in the <h1> tag
    story_dict = {}
    for i in range(len(stories)): # Get all stories
        pars = []
        first = stories[i]
        text = ""
        try:
            second = stories[i+1]
            for tag in first.find_all_next():
                if tag == second:
                    break
                else:
                    if tag.name == 'h2' or tag.name == 'p': # Subheadings for Novellas and Long Stories are h2 tags; all else is p tags
                        pars.append(tag)
        except IndexError: # This is to handle the idea of first/second and last
            for tag in first.find_all_next():
                if tag.name == 'h2' or tag.name == 'p':
                    pars.append(tag)
        lines = []
        for line in pars: # each line is an html code block
            line_text = line.get_text().replace("\n", " ") # These were encoded in the <p> but get rid of them
            if not line_text: # Get rid of empty tags; get rid of leading whitespace
                continue
            elif line_text[0] == " ":
                string = line_text[1:]
                lines.append(f"{string}")
            else:
                string = line_text
                lines.append(f"{string}")
        newlines = []
        for line in lines:
            newline = line.replace('“', '"').replace('”', '"').replace("’", "'").replace("‘", "'").replace("—", "--") # Get rid of anything fancy and convert to plaintext
            newlines.append(newline)
        story_title = str(first.get_text()).replace("\\n", "").replace("\\'", "'").strip() # Clean up the title
        story_dict[story_title] = newlines
    epubs[title] = story_dict

##### DATA CLEANING #####

skips = ['introduction', 'preface', 'foreword', 'table of contents', 'notes', 'missing parts'] # Stuff found in collections that aren't stories

# Make dictionary of just the short stories
short_stories = {}
for title, story in texts.items():
    short_stories[title] = (story, f"{title}")

for volume in epubs:
    for title, story in epubs[volume].items():
        if title.lower() in skips:
            continue
        else:
            short_stories[title] = (story, f"{volume}")
print("CREATED: Dictionary of stories")
    
          
# These three stories had spelling and format errors
short_stories["Impostor"] = short_stories["Imposter"]
short_stories["A Terran Odyssey"] = short_stories["A Tehran Odyssey"] 
short_stories["The Story to End All Stories for Harlan Ellison's Anthology Dangerous Visions"] = short_stories["The Story to End All Stories for Harlan Ellison's Anthology Dangerous\nVisions"]
del short_stories["Imposter"]
del short_stories["A Tehran Odyssey"] 
del short_stories["The Story to End All Stories for Harlan Ellison's Anthology Dangerous\nVisions"]

##### METADATA DATAFRAME #####


df = pd.read_csv('source_files/ss_year.csv') # Read in csv with titles and year, made manually from the notes of the volumes & wikipedia
# New columns
df['Author'] = "Philip K. Dick"
df['File'] = ''
df['Source'] = ''
df['Source File Type'] = ''

# Fill columns with File, Notes, and Source
new_order = ['File', 'Title', 'Source', 'Year Written', 'Year Published', 'Author', 'Source File Type', 'Notes']
df = df[new_order]
for title, story in short_stories.items():
    file = title.lower().replace(" ", "_").replace("'", "").replace(".","").replace("?", "").replace("!", "").replace(":", "").replace(",", "")
    filename = f"{file}.txt"
    for index, row in df.iterrows():
        if row['Title'].lower() == title.lower():
            df.at[index, 'File'] = filename
            df.at[index, 'Source'] = story[1]
            if row['Title'] == "Impostor" or row['Title'] == "A Terran Odyssey":
                df.at[index, 'Notes'] = 'Modified Title'
            if row['Title'] in texts:
                df.at[index, 'Source File Type'] = 'txt'
                df.at[index, 'Notes'] = 'Missing from Vol. 3, sourced elsewhere'
            else:
                df.at[index, 'Source File Type'] = 'epub'

# Get rid of source info from dict
short_stories_export = {}
for title, story in short_stories.items():
    short_stories_export[title] = story[0]

df_sort = df.sort_values(by='File')
print("CREATED: Metadata CSV")

##### OUTPUTS #####

os.makedirs("corpus/text_files", exist_ok=True)  
os.makedirs("corpus/meta_files", exist_ok=True)  

# Every text file will be the lowercase title, stripped of punctuation and spaces, as the filename. The first line will be the full title; the text will start after a few newlines
for title, story in short_stories_export.items():
    file = title.lower().replace(" ", "_").replace("'", "").replace(".","").replace("?", "").replace("!", "").replace(":", "").replace(",", "")
    filename = f"corpus/text_files/{file}.txt"
    with open(filename, "w", encoding="utf-8") as n:
        n.write(f"{title}\n\n\n")
        for line in story:
            n.write(f"{line}\n\n")
print("WRITTEN: Stories to txt in text_files")

# CSV with metadata from dataframe
df_sort.to_csv('corpus/meta_files/metadata.csv', index=False)
print("WRITTEN: Metadata csv in meta_files")

# JSON with all stories
with open('corpus/meta_files/all_stories.json', 'w', encoding="utf-8") as j:
    json.dump(short_stories_export, j, indent=4)
print("WRITTEN: Full json in meta_files")