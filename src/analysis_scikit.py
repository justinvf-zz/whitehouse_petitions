from heapq import nlargest
import config
import util
import os
import pandas as pd


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
        for filename in os.glob(os.path.join(config.NPR_DATA_DIR, '*gz')):
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
    return pd.read_csv(counts_path, delim='\t', lineterminator='\n')

def show_best_articles(article_data, petition_data, article_scores, petition_number=None):
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
