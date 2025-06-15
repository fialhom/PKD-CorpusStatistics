# PKD-CorpusStatistics

Corpus Statistics and Analysis Functions for Short Stories by Philip K Dick

Note: I have not included any text files due to wishing to avoid potential copyright flags or infringements

## epub_to_txt
This program converts epub collections of Philip K Dick to cleaned text files, with consistent encoding and structure.

## txt_to_TEI
This program converts the formatted txt files (contained in JSON) to TEI, using metadata contained in a custom metadata CSV scraped from various sources to provide information on the stories. The TEI was processed using PhiloLogic in order to create a concordance and key-word trend and analysis.

## process
This program processes the txt files and vectorizes using TFIDF vectorization with pre-processing (lemmatization, entity and stop word removal, part of speech filtering), to maximize successful and interpretable results; the stories are then analyzed for topic models, similarities, and word frequencies.
