import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from analysis_scikit import (to_top_n, show_best_articles, load_petitions,
                             load_all_articles, load_petition_counts,
                             get_all_json)

from util import save_to_disk

# Number of articles needed in order to generate a blob.
MIN_ARTICLES = 10

all_articles = load_all_articles()

full_article_texts = [' '.join((a['title'],
                                ' '.join(a['paragraphs']),
                                a['teaser'])) for a in all_articles]


petitions = load_petitions()

petition_texts = (petitions.title + ' ' + petitions.body).str.replace('\\\\n', ' ')

# TODO: play with ngram range
    # v = TfidfVectorizer(strip_accents='ascii',
    #                     ngram_range=(1,2),
    #                     max_df=.8,
    #                     min_df=min_df,
    #                     use_idf=True,
    #                     stop_words='english')
v = TfidfVectorizer(stop_words='english', ngram_range=(1,2), use_idf=True)

# Just fit to the petitions
v.fit(petition_texts)

transformed_articles = v.transform(full_article_texts)

transformed_petitions = v.transform(petition_texts)

#to_top_n(transformed_articles, n=200)
#to_top_n(transformed_petitions, n=200)

article_scores = transformed_petitions * transformed_articles.T

to_top_n(article_scores, n=50)

# Print out some stuff... this is working!!
show_best_articles(all_articles, petitions, article_scores, petition_number=10)

show_best_articles(all_articles, petitions, article_scores, petition_number=100)

petition_counts = load_petition_counts()

all_clean_blobs = get_all_json(all_articles, petitions, article_scores, petition_counts)

# Restrict to 2013 blobs with a decent amount of articles
blob_paths = []

URL_OUTPUT_PATH = '/post-files/20140101-whitehouse-petitions/blobs'

i = 0
for b in all_clean_blobs:
    if b['petition_date'].startswith('2013'):
        if type(b['petition_close']) == float:
            b['petition_close'] = None
        b['articles'] = [a for a in b['articles'] if a['date'].startswith('2013')]
        if len(b['articles']) >= MIN_ARTICLES:
            filename = 'blob-{}.json'.format(i)
            save_to_disk('blobs/' + filename, b, compress=False)
            blob_paths.append({'fragment': str(abs(hash(b['petition_title']))),
                               'url': '{}/{}'.format(URL_OUTPUT_PATH, filename)})
            i += 1

save_to_disk('blobs/all_petitions.json', blob_paths, compress=False)
