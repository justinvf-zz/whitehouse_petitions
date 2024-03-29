from heapq import nlargest
import config
import util
import os
from glob import glob
import pandas as pd
from dateutil import parser


def to_top_n(csr_matrix, n=10):
    """Get a matrix with only the n largest entries per row."""
    data = csr_matrix.data
    indices = csr_matrix.indptr
    for i in range(len(indices) - 1):
        (row_start, row_end) = (indices[i], indices[i + 1])
        if row_start == row_end:
            continue
        nth_largest = nlargest(n, data[row_start:row_end])[-1]
        for i in range(row_start, row_end):
            if data[i] < nth_largest:
                data[i] = 0
    csr_matrix.eliminate_zeros()


def load_all_articles():
    all_blob_path = os.path.join(config.NPR_DATA_DIR, 'all_articles.gz')
    if not os.path.exists(all_blob_path):
        all_blobs = []
        for filename in glob(os.path.join(config.NPR_DATA_DIR, '*gz')):
            all_blobs.extend(util.load_from_disk(filename))
        util.save_to_disk(all_blob_path, all_blobs)
    else:
        all_blobs = util.load_from_disk(all_blob_path)
    return all_blobs

def load_petitions():
    texts_path = os.path.join(config.ROOT_DATA_DIR, 'petition_texts.tsv')
    return pd.read_csv(texts_path, sep='\t', lineterminator='\n')

def load_petition_counts():
    counts_path = os.path.join(config.ROOT_DATA_DIR, 'signatures_per_day.tsv')
    return pd.read_csv(counts_path, sep='\t', lineterminator='\n')

def show_best_articles(article_data, petition_data, article_scores,
                       petition_number=None):
    r = article_scores.getrow(petition_number)
    nonzero_entries = list(r.nonzero()[1])
    nonzero_entries.sort(key=lambda x : r[0,x], reverse=True)
    
    print('PETITION TITLE: \n{}'.format(petition_data.title[petition_number]))
    print('ARTICLES')
    for i in range(10):
        article_index = nonzero_entries[i]
        score = r[0, article_index]
        if score > 0:
            print('SCORE: {} ARTICLE TITLE: {}'.format(
                score, article_data[article_index]['title']))


def get_short_link(links):
    for l in links:
        if 'http://n.pr' in l:
            return l
    # If nothng else..
    return l

def get_reporting_json(article_data, petition_data, article_scores,
                       petition_counts,
                       petition_number=None, article_score_lower_bound=.145):
    r = article_scores.getrow(petition_number)
    nonzero_entries = list(r.nonzero()[1])
    nonzero_entries.sort(key=lambda x : r[0,x], reverse=True)

    to_return = {}
    petition = petition_data.ix[petition_number]
    petition_key = petition['id']
    to_return['petition_title'] = petition['title']
    to_return['petition_text'] = petition['body']
    to_return['petition_url'] = petition['url']
    to_return['petition_date'] = petition['created']
    to_return['petition_close'] = petition['closed'] or None

    date_counts = petition_counts[petition_counts.petition_id == petition_key][['day', 'number']]

    to_return['signature_counts'] = [{'date': r[1]['day'], 'count': r[1]['number']}
                                 for r in date_counts.iterrows()]

    article_list = []
    to_return['articles'] = article_list

    for article_index in nonzero_entries:
        score = r[0, article_index]
        if score > article_score_lower_bound:
            article = article_data[article_index]
            article_list.append({
                'score': score,
                'title': article['title'],
                'date': article['date'],
                'teaser': article['teaser'],
                'link': get_short_link(article['links'])})

    return to_return

def get_all_json(article_data, petition_data, article_scores,
                 petition_counts, petition_number=None, article_score_lower_bound=.145,
                 before_days=60, after_days=100, min_articles=5, trim_it=False):

    to_return = []
    for i in range(len(petition_data)):
        blob = get_reporting_json(article_data, petition_data, article_scores,
                                  petition_counts,
                                  petition_number=i,
                                  article_score_lower_bound=article_score_lower_bound)
        parsed_petition_date = parser.parse(blob['petition_date'])

        new_articles = []
        for a in blob['articles']:
            # Hack to remove timezone, but fine for our needs...
            article_date = parser.parse(a['date']).replace(tzinfo=None)
            days_diff = (parsed_petition_date - article_date).days
            if -before_days < days_diff < after_days:
                new_articles.append(a)
                a['date'] = article_date.strftime('%Y-%m-%d')
                if trim_it:
                    a['teaser'] = trim_text(a['teaser'], 150)

        if len(new_articles) >= min_articles:
            blob['articles'] = new_articles
            to_return.append(blob)
        if trim_it:
            blob['petition_text'] = trim_text(blob['petition_text'], 150)

    return to_return
