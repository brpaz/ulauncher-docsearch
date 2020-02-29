"""
Module responsible for search into docs
"""

import json
import os
import logging
from algoliasearch.search_client import SearchClient

DEFAULT_DOC_IMAGE = 'images/icon.png'

LOGGING = logging.getLogger(__name__)

DOCSETS_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data',
                                 'docsets.json')


class DocSearch:
    """ Searches Documentation On DocSearch based applications """
    def __init__(self):
        """ Class constructor """
        self.docsets = {}

        with open(DOCSETS_FILE_PATH, 'r') as data:
            self.docsets = json.load(data)

    def get_available_docs(self, filter_term):
        """ Returns a list of available docs """
        docs = []
        for key, value in self.docsets.items():
            docs.append({
                'key': key,
                'name': value['name'],
                'description': value['description'],
                'icon': value['icon'],
                'url': value['url']
            })

        if filter_term:
            docs = [
                x for x in docs if filter_term.lower() in x['name'].lower()
            ]

        return docs

    def has_docset(self, key):
        """ Checks if the specified docset exists """
        return key in self.docsets

    def get_docset(self, key):
        """ Returns the details from a docset with the specified key passed as argument """

        if key in self.docsets.keys():
            return self.docsets[key]

        return None

    def search(self, docset, term):
        """ Searches a term on a specific docset and return the results """
        docset = self.get_docset(docset)

        if not docset:
            raise ValueError("The specified docset is not known")

        algolia_client = SearchClient.create(docset['algolia_application_id'],
                                             docset['algolia_api_key'])

        index = algolia_client.init_index(docset['algolia_index'])
        search_results = index.search(term)

        if not search_results['hits']:
            return []

        items = []
        for hit in search_results['hits']:
            title, description = self.parse_item_description(hit)
            items.append({
                'url': hit['url'],
                'title': title,
                'icon': docset['icon'],
                'category': description
            })

        return items

    def parse_item_description(self, hit):
        """ Returns the text to display as result item title """
        hierarchy = hit['hierarchy'].values()

        # Filter the list by removing the empty values
        res = [i for i in hierarchy if i]

        if len(res) < 2:
            return res[0], ""

        # The last element found will be the description and the previous one the title.
        return res[-1], ' -> '.join(res[:-1])
