"""
This module will crawl the NPR news feed to get news articles.

The API is documented here:
http://www.npr.org/templates/apidoc/inputReference.php

We will just use a simple subset to get the news for each day.
"""

from dateutil import parser
from config import NPR_API_KEY, NPR_SLEEP, NPR_DATA_DIR
from httplib2 import Http
from json import loads
import time
from datetime import timedelta, datetime
from util import save_to_disk
import os
from optparse import OptionParser


NEWS_TOPIC = 1001

URL_TEMPLATE = ('http://api.npr.org/query?'
                'id={topic_id}&fields=title,text,teaser,storyDate&'
                'date={date}&startNum={offset}&numResults=20'
                '&dateType=story&output=JSON'
                '&apiKey={api_key}')

# One instance so that we can conserve HTTP connections via httplib2 pooling.
H = Http()


def get_paragraphs(story):
    """Helper method to get the text from all paragraphs in an article."""
    # Stip out our API key...
    return [p['$text'] for p in story['text']['paragraph']
            if '$text' in p]


def get_links(story):
    return [l['$text'] for l in story['link']
            if '$text' in l and 'apiKey=' not in l['$text']]


def url_for_date(date, page=0, count=20, topic_id=NEWS_TOPIC):
    """Return the URL for accessing a chunk of stories.

    Parameters:
    api_key: The key for accessing the NPR api.
    topic: The NPR topic id. See 
    offset: the offset into the results
    count: number of results to return.
    """
    return URL_TEMPLATE.format(api_key=NPR_API_KEY,
                               count=count,
                               offset=(page * count),
                               date=date.strftime('%Y-%m-%d'),
                               topic_id=topic_id)


def parse_date(story):
    parsed = parser.parse(story['storyDate']['$text'])
    return parsed.isoformat()

def articles_for_url(url):
    """Return all articles for a given URL."""
    (response, content) = H.request(url)
    if response['status'] != '200':
        return ()

    parsed = loads(content.decode("utf-8"))
    stories = parsed['list'].get('story', [])
    return [{'title': story['title']['$text'],
             'paragraphs': get_paragraphs(story),
             'links' : get_links(story),
             'date': parse_date(story),
             'teaser': story['teaser']['$text']}
            for story in stories if 'text' in story]


def articles_for_date(date):
    """Return a list of articles, each its own dictionary."""
    date_articles = []
    page = 0
    last_length = 1  # For tracking if we got all for a date.
    while True:
        time.sleep(NPR_SLEEP)
        url = url_for_date(date, page=page)
        page_articles = articles_for_url(url)
        date_articles.extend(page_articles)
        if len(page_articles) < last_length:
            break
        last_length = len(page_articles)
        page += 1
    return date_articles


def article_filename(date, data_dir=NPR_DATA_DIR):
    filename = '{:%Y-%m-%d}.gz'.format(date)
    return os.path.join(data_dir, filename)


def crawl_all_articles(num_days, start_date):
    """Crawls num_days articles, going forwards from start_date."""
    for i in range(num_days):
        article_date = start_date + timedelta(days=i)
        filename = article_filename(article_date)
        save_to_disk(filename, articles_for_date(article_date))


if __name__ == '__main__':
    op = OptionParser()   
    op.add_option('--start_date',
                  dest='start_date',
                  type=str,
                  help='Start date in YYYY-mm-dd format')
    op.add_option('--num_days',
                  dest='num_days',
                  type=int,
                  default=10,
                  help='Number of days to crawl, starting at --start_date')

    (opts, args) = op.parse_args()
    if not opts.start_date:
        start_date = datetime.today() - timedelta(days=10)
    else:
        start_date = datetime.strptime(opts.start_date, '%Y-%m-%d')

    crawl_all_articles(opts.num_days, start_date)
