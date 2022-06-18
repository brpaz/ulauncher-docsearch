from ulauncher.config import CACHE_DIR
import requests
import logging
import json
import os

logger = logging.getLogger(__name__)

CACHE_FOLDER_PATH = os.path.join(CACHE_DIR, 'ulauncher-docsearch',
                                 'mkdocs-indexes')


class MkDocsIndexError(Exception):
    pass


class MkDocsIndexer(object):

    def index(self, docset_key, docset):
        url = docset["search_index_url"]

        r = requests.get(url)
        if r.status_code != 200:
            raise MkDocsIndexError(
                "Error downloading mkdocs index for %s. HTTP error: %s" %
                (docset_key, r.status_code))

        data = r.json()

        if "docs" not in data:
            return

        items = []

        for doc in data["docs"]:
            items.append(self.map_item(doc))

        index_file = self.get_index_file_path(docset_key)
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(items, f)

    def get_index_file_path(self, docset_key):
        index_filename = "%s.json" % docset_key

        if not os.path.exists(CACHE_FOLDER_PATH):
            os.makedirs(CACHE_FOLDER_PATH)

        return os.path.join(CACHE_FOLDER_PATH, index_filename)

    def map_item(self, data):
        return {
            'title': data["title"],
            'description': data["location"],
            'text': self.trim_string(str(data["text"]), 60)
        }

    def trim_string(self, s: str, limit: int, ellipsis='…') -> str:
        s = s.strip()
        if len(s) > limit:
            return s[:limit - 1].strip() + ellipsis

        return s
