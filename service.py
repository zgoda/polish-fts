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


stemmer = StempelStemmer.default()


class PlainTextMediaHandler(media.BaseHandler):

    def deserialize(self, stream, content_type, content_length):
        return stream.read().decode('utf-8')

    def serialize(self, media, content_type):
        return media.encode('utf-8')


class DocResource:

    def on_post(self, req: Request, resp: Response):
        text = req.media
        stems = [stemmer.stem(word) for word in tokenise(text)]
        stems = [s for s in stems if s]
        doc = DocIndex.create(text=' '.join(stems), source=text)
        resp.body = json.dumps({'docid': doc.rowid})
        resp.status = falcon.HTTP_201


class SearchResource:

    def on_get(self, req: Request, resp: Response):
        q = req.params.get('q', '')
        if q:
            stems = [stemmer.stem(word) for word in tokenise(q)]
            docs = DocIndex.search(' '.join(stems))
            resp.media = {d.rowid: d.source for d in docs}
        else:
            resp.status = falcon.HTTP_404


doc_resource = DocResource()
search_resource = SearchResource()

app = falcon.API()
app.req_options.media_handlers['text/plain'] = PlainTextMediaHandler()
app.add_route('/document', doc_resource)
app.add_route('/search', search_resource)


if __name__ == '__main__':
    run_simple(
        '127.0.0.1', 5000, app, use_reloader=True, use_debugger=False, use_evalex=True
    )
