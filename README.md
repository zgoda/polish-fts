# Full Text Search helpers for Polish language

This is research project to determine usability of all available stemmer implementations for Polish language in context of augmenting simple search engines that do not support Polish language directly. Apart of search engines based on Lucene (Solr and ElasticSearch) none of search engines supports full text search in Polish.

Intended usage model is to store only stems and then apply stemmed queries so there's non-trivial requirement that the implementation a) does not take too much time to load or b) does not eat too much RAM if it stays preloaded in running process. As a baseline full text search engine SQLite FTS5 table with simple tokeniser will be used. Since both MySQL and Postgres so not support anything more, the overhead added by helper code will be the same for both database engines.

## The idea

The code will be modeled after usual web application that processes requests and returns responses. The application code will stay in memory for some time and will be restarted after each 100 requests (no matter read or write). Data ingress will be performed by external/background task resembling queue handler, which is the most commonly used pattern in web applications. The eggress will be direct.

## Currently evaluated stemmers

* [pystempel](https://github.com/dzieciou/pystempel), Python implementation of 1st fully functional Polish stemmer Stempel
* Polish [implementation](https://github.com/Tutanchamon/pl_stemmer) of widely used Porter stemming algoithm

Additionally [Eugenia Oshurko's FST-based stemmer](https://github.com/eugeniashurko/polish-stem) for Polish will be evaluated but since the implementation does not have any accompanied license it will not be included in helper's reference implementation.

## Implementation

As a refresher and to not go easy way this will be implemented in Twisted.

It can't be any better.
