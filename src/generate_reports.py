from sklearn.feature_extraction.text import TfidfVectorizer

from analysis_scikit import to_top_n, show_best_articles, load_petitions, load_all_articles

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
