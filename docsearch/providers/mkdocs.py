import functools
import os
import json
from .base import BaseProvider
from .constants import PROVIDER_MKDOCS

from docsearch.indexers.mkdocs import CACHE_FOLDER_PATH


class MkDocsProvider(BaseProvider):

    def get_name(self):
        return PROVIDER_MKDOCS

    def search(self, docset_key, docset, query):

        data = self.read_mkdocs_index_file(docset_key)

        results = []
        for item in data:
            if query.lower() in item["title"].lower():
                results.append({
                    'url':
                    "{}/{}".format(docset["url"], item["description"]),
                    'title':
                    item["title"],
                    'icon':
                    docset['icon'],
                    'category':
                    item['description'],
                })

        return results

    @functools.lru_cache(maxsize=10)
    def read_mkdocs_index_file(self, docset_key):
        file_path = os.path.join(CACHE_FOLDER_PATH, "%s.json" % docset_key)
        with open(file_path) as f:
            return json.load(f)
