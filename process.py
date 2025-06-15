print("PHILIP K DICK CORPUS MODELING\n")
### IMPORTS ###
print("Loading Imports ...", end=' ', flush=True)
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
from sklearn.decomposition import NMF

import pandas as pd
import spacy

import os

### Model Settings
nlp = spacy.load("en_core_web_sm")
vectorizer = CountVectorizer()
tfvectorizer = TfidfVectorizer(max_df=0.7)
nmf = NMF(n_components=20, max_iter=500) 
classifier = MultinomialNB()
stopwords = nlp.Defaults.stop_words
print('done.')

########## OLD TEST FUNCTION ##########
# This was the first way I iterated through various pre-processing functions; I placed it all in a dummy function just so it wouldnt run, but could be viewed

def old_function_placeholder():
    theology = ["christ", "god", 'jesus', 'mary', 'joseph', 'holy', 'abraham', 'moses', 'spirit']
    def preprocess_OLD(text):
        try:
            doc = nlp(text)
        except ValueError:
            nlp.max_length = len(text) + 1
            doc = nlp(text)
        high_filter = [] # Filers out stops, names, and parts of speech
        med_filter = [] # Filters out stops, entities (date, name, orgs)
        low_filter = [] # Filters out stops
        for token in doc:
            if token.lemma_ not in stopwords:# and token.ent_type_ == "":
                low_filter.append(str(token.lemma_))
                if token.ent_type_ == "":
                    med_filter.append(str(token.lemma_))
                    if  token.pos_ in ("NOUN", "VERB", "ADJ", "ADV", "INTJ"):
                        high_filter.append(str(token.lemma_))
                elif token.lemma_ in theology:
                    med_filter.append(str(token.lemma_))
                    if  token.pos_ in ("NOUN", "VERB", "ADJ", "ADV", "INTJ"):
                        high_filter.append(str(token.lemma_))
                    
            
            
        high = " ".join(high_filter)
        med = " ".join(med_filter)
        low = " ".join(low_filter)
        
        return (high, med, low)

    corpus = {"high": [], "med": [], "low": []}
    filenames = []
    count = 0
    for file in os.scandir("text_files"):
        title = file.name.replace(".txt", "")
        print(f"{title} ...", end=" ", flush=True)
        with open(file.path) as i_file:
            text = i_file.read()
        high, med, low = preprocess_OLD(text)
        corpus["high"].append(high)
        corpus["med"].append(med)
        corpus["low"].append(low)
        filenames.append(title)
        print("!")
        count+=1
        if count == 10:
            break
        
    def process(select):
        vcorp = vectorizer.fit_transform(corpus[select])
        tfvcorp = tfvectorizer.fit_transform(corpus[select])
        sim = cosine_similarity(tfvcorp)

        df_v = pd.DataFrame(vcorp.toarray(), index=filenames, columns=vectorizer.get_feature_names_out())
        df_sim = pd.DataFrame(sim, index=filenames, columns=filenames)
        df_tf = pd.DataFrame(tfvcorp.toarray(), index=filenames, columns=tfvectorizer.get_feature_names_out())
        
        df_v.to_csv(f"{select}_vector_matrix.csv")
        df_tf.to_csv(f"{select}_tfidf_matrix.csv")
        df_sim.to_csv(f"{select}_sim_matrix.csv")
        return (df_v, df_tf, df_sim)




    m_v, m_tf, m_sim = process("med")
    h_v, h_tf, h_sim = process("high")
    l_v, l_tf, l_sim = process("low")

########## PREPROCESSING 

def preprocess(text):
    keepers = ["christ", "god", 'jesus',  'holy', 'spirit', 'heaven', 'hell', 'purgatory', "faith", "church", "pray"]
    try:
        doc = nlp(text)
    except ValueError:
        nlp.max_length = len(text) + 1
        doc = nlp(text)
    filter = [] 
    for token in doc:
        if token.lemma_.lower() in keepers:
            filter.append(str(token.lemma_))
        elif token.lemma_ not in stopwords:
            if token.ent_type_ == "":
                if  token.pos_ in ("NOUN", "ADJ", "VERB", "ADV"):
                    filter.append(str(token.lemma_))

    words = " ".join(filter)
    return words

# Parse text files
def parse(dir):
    corpus = []
    filenames = []
    count = 1
    for file in os.scandir(dir):
        title = file.name.replace(".txt", "")
        print(f"[{count}/118]\t{title} ...", end=" ", flush=True)
        with open(file.path) as i_file:
            text = i_file.read()
        corpus.append(preprocess(text))
        filenames.append(title)
        print("!")
        count+=1
        if count == 10:
            continue # I would set this to break to quickly run iterations on the function
    return (corpus, filenames)

########## VECTORIZATION

# Function to run the vectors
def process(corpus, filenames):
    vcorp = vectorizer.fit_transform(corpus)
    tfvcorp = tfvectorizer.fit_transform(corpus)
    sim = cosine_similarity(tfvcorp)

    df_v = pd.DataFrame(vcorp.toarray(), index=filenames, columns=vectorizer.get_feature_names_out())
    df_sim = pd.DataFrame(sim, index=filenames, columns=filenames)
    df_tf = pd.DataFrame(tfvcorp.toarray(), index=filenames, columns=tfvectorizer.get_feature_names_out())
    
    print('Saving ... ', end='', flush=True)
    df_v.to_csv("vector_matrix.csv")
    df_tf.to_csv("tfidf_matrix.csv")
    df_sim.to_csv("sim_matrix.csv")
    
    return ((df_v, df_tf, df_sim), (vcorp, tfvcorp, sim))

########## RUN THE MODELS

def main():
    # Run NLP on all stories; vectorize

    # Preprocess
    print("NLP Preprocessing ... ", flush=True)
    corpus, filenames = parse("text_files")
    print("DONE.\n")
    
    # Vectorize
    print("Vectorizing ... ", end='', flush=True)
    databases, vectors = process(corpus, filenames)
    print('done.')
    df_v, df_tf, df_sim = databases
    vcorp, tfvcorp, sim = vectors
    
    # Count
    print("Counting ... ", end='', flush=True)
    most_common = df_v.sum().sort_values(ascending=False).head(20)
    mean_freq = df_v.mean().sort_values(ascending=False).head(20)
    print('done.')
    
    # Topic Model
    print("Topic Modeling ... ", end='', flush=True)
    topic_dist = nmf.fit_transform(tfvcorp)
    topic_df = pd.DataFrame(nmf.components_, columns=tfvectorizer.get_feature_names_out())
    print('done.')
    
    # Similarity Matrix
    print('Similarity Matrixing ... ', end='', flush=True)
    sim_matrix_nmf = cosine_similarity(topic_dist)
    sim_matrix_df = pd.DataFrame(sim_matrix_nmf, index=filenames, columns=filenames)
    print('done.')
    textfile = "results.txt"
    
    # PRINT TO TXT FILE (because why not)
    print('Printing ... ', end='', flush=True)
    with open(textfile, "w", encoding="utf8") as f:
        f.write("!------------------------------------------------------!\n")
        f.write("!----- PHILIP K DICK SHORT STORIES CORPUS RESULTS -----!\n")
        f.write("!------------------------------------------------------!\n\n")
        f.write("==================== CORPUS STATS\n\n")
        f.write("--- WORD COUNT\n\n")
        for word, count in most_common.items():
            f.write(f"{word} -- {count}\n")
        f.write("\n--- WORD FREQUENCY\n\n")
        for word, count in mean_freq.items():
            f.write(f"{word} -- {count:.2f}\n")
        f.write("\n--- CORPUS TOPICS\n\n")
        for topic, row in topic_df.iterrows():
            top_10 = ", ".join([str(x) for x in row.sort_values(ascending=False).head(10).index])
            f.write(f"{topic}: {top_10}\n")
        f.write("\n==================== STORIES STATS\n\n")
        f.write("--- WORD FREQUENCY\n")
        for story, row in df_tf.iterrows():
            f.write(f"\n## {story} ##\n")
            for word, weight in row.sort_values(ascending=False).head(10).items():
                f.write(f"{word} -- {weight:.2f}\n")
        f.write("\n--- STORY SIMILARITY\n")
        for col, row in sim_matrix_df.iterrows():
            top3 = row.sort_values(ascending=False).head(4)
            top3 = top3[1:]
            f.write(f"\n{col} is most similar to:\n")
            for story, value in top3.items():
                f.write(f"\t{value:.2f} --- {story}\n")
    print('done.\n\nSEE: results.txt')  
       
# run
main()