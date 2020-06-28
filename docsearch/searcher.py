"""
Module responsible for search into docs
"""

import json
import os
import logging
from algoliasearch.search_client import SearchClient

DEFAULT_DOC_IMAGE = 'images/icon.png'

LOGGING = logging.getLogger(__name__)

DOCSETS_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data',
                                 'docsets.json')

USER_DOCSETS_PATH = os.path.join(os.path.expanduser("~"), ".config",
                                 "ulauncher", "ext_preferences", "docsearch")


class Searcher:
    """ Searches Documentation On DocSearch based applications """
    def __init__(self):
        """ Class constructor """
        self.docsets = {}

        self.load_default_docsets()
        self.load_user_docsets()

    def load_default_docsets(self):
        """ Loads default docsets into memory """
        with open(DOCSETS_FILE_PATH, 'r') as data:
            self.docsets = json.load(data)

    def load_user_docsets(self):
        """ Loads custom user docsets into memory """
        if not os.path.isdir(USER_DOCSETS_PATH):
            return

        docsets_file = os.path.join(USER_DOCSETS_PATH, "docsets.json")

        if not os.path.isfile(docsets_file):
            return

        with open(docsets_file, 'r') as data:
            user_docsets = json.load(data)

            for key, docset in user_docsets.items():
                icon = os.path.join(USER_DOCSETS_PATH, docset["icon"])
                if not os.path.isfile(icon):
                    icon = "images/icon.png"
                user_docsets[key]["icon"] = icon

            self.docsets.update(user_docsets)

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
        if key in self.docsets:
            return self.docsets[key]

        return None

    def search(self, docset_key, term):
        """ Searches a term on a specific docset and return the results """
        docset = self.get_docset(docset_key)

        if not docset:
            raise ValueError("The specified docset is not known")

        algolia_client = SearchClient.create(docset['algolia_application_id'],
                                             docset['algolia_api_key'])

        index = algolia_client.init_index(docset['algolia_index'])

        search_results = index.search(
            term, self.get_search_request_options_for_docset(docset_key))

        if not search_results['hits']:
            return []

        return self.process_results(docset_key, docset, search_results["hits"])

    def process_results(self, docset_key, docset_data, results):
        """ Processes the results of Algolia Search """

        items = []
        for hit in results:
            # Prisma documentation seems to have a different format. Is it a new version of Docsearch?
            # For now, parse Prisma differently, generalize If this format found in more places.
            if docset_key == "prisma":
                title = hit["title"]
                description = hit["heading"]
                url = docset["url"] + hit["path"]
            else:
                title, description = self.parse_item_description(hit)
                url = hit['url']

            items.append({
                'url': url,
                'title': title,
                'icon': docset_data['icon'],
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

    def get_search_request_options_for_docset(self, docset):
        """
        Allow to specify custom search options for a specific docset
        Parameters:
            docset (string): The identifier of the docset.
        """
        opts = {}

        if docset == 'nuxt':
            opts = {"facetFilters": ["tags:en"]}

        if docset == "bootstrap":
            opts = {"facetFilters": ["version:4.5"]}

        if docset == "vuex":
            opts = {"facetFilters": ["lang:en-US"]}

        if docset == "vue-router":
            opts = {"facetFilters": ["lang:en-US"]}

        if docset == "strapi":
            opts = {"facetFilters": ["lang:en-US"]}

        return opts
