import argparse
import json
import os
import string
from typing import List

import falcon
from dotenv import find_dotenv, load_dotenv
from falcon import Request, Response, media
from playhouse.sqlite_ext import FTS5Model, SearchField, SqliteExtDatabase
from stempel import StempelStemmer
from werkzeug.serving import run_simple

load_dotenv(find_dotenv())

stemmer = StempelStemmer.default()

db = SqliteExtDatabase(None)


class DocIndex(FTS5Model):
    text = SearchField()
    source = SearchField(unindexed=True)

    class Meta:
        database = db


db.init(os.getenv('DB_FILENAME'), pragmas={
    'journal_mode': 'wal',
    'cache_size': -1 * 64000,
    'synchronous': 0,
})
db.create_tables([DocIndex])


def tokenise(text: str) -> List[str]:
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return [w for w in text.split() if len(w) > 2]


def to_stems(text: str) -> str:
    stems = [stemmer.stem(word) for word in tokenise(text)]
    stems = [s for s in stems if s]
    return ' '.join(stems)


def index_document(stemmed: str, orig: str) -> DocIndex:
    if db.is_closed():
        db.connect()
    doc = DocIndex.create(text=stemmed, source=orig)
    return doc


def index_local_file(path: str):
    with open(path) as fp:
        text = fp.read()
    stems = to_stems(text)
    index_document(stems, text)


def index_local_content(path: str):
    if os.path.isfile(path):
        index_local_file(path)
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            index_local_file(os.path.join(path, filename))


class PlainTextMediaHandler(media.BaseHandler):

    def deserialize(self, stream, content_type, content_length):
        return stream.read().decode('utf-8')

    def serialize(self, media, content_type):
        return media.encode('utf-8')


class DocResource:

    def on_post(self, req: Request, resp: Response):
        text = req.media
        stemmed = to_stems(text)
        doc = index_document(stemmed, text)
        resp.body = json.dumps({'docid': doc.rowid})
        resp.status = falcon.HTTP_201


class SearchResource:

    def on_get(self, req: Request, resp: Response):
        q = req.params.get('q', '')
        if q:
            stems = to_stems(q)
            docs = DocIndex.search(stems)
            resp.media = {d.rowid: d.source for d in docs}
        else:
            resp.status = falcon.HTTP_404


doc_resource = DocResource()
search_resource = SearchResource()


class PeeweeConnectionMiddleware(object):

    def process_request(self, req, resp):
        db.connect(reuse_if_open=True)

    def process_response(self, req, resp, resource, req_succeeded):
        if not db.is_closed():
            db.close()


def make_app() -> falcon.API:
    app = falcon.API(middleware=[
        PeeweeConnectionMiddleware(),
    ])
    app.req_options.media_handlers['text/plain'] = PlainTextMediaHandler()
    app.add_route('/document', doc_resource)
    app.add_route('/search', search_resource)
    return app


def get_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--index', help='location of content to be indexed')
    return parser.parse_args()


def main():
    opts = get_options()
    if opts.index:
        index_local_content(opts.index)
    else:
        app = make_app()
        run_simple(
            '127.0.0.1', 5000, app, use_reloader=True, use_debugger=False,
            use_evalex=True,
        )


if __name__ == '__main__':
    main()
