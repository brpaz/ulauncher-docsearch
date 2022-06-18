"""
Module responsible for search into docs
"""

import json
import os
import logging
import functools
from docsearch.mapper import DefaultMapper, VercelMapper, PrismaMapper, TerraformMapper, WebDevMapper
from docsearch.indexers.mkdocs import CACHE_FOLDER_PATH
from algoliasearch.search_client import SearchClient
from algoliasearch.exceptions import AlgoliaException

DEFAULT_DOC_IMAGE = 'images/icon.png'

LOGGING = logging.getLogger(__name__)

DOCSETS_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data',
                                 'docsets.json')

USER_DOCSETS_PATH = os.path.join(os.path.expanduser("~"), ".config",
                                 "ulauncher", "ext_preferences", "docsearch")

DOCS_PROVIDER_ALGOLIA_DOCSEARCH = "algolia"
DOCS_PROVIDER_MKDOCS = "mkdocs"


class Searcher:
    """ Class that handles the documentation search """

    def __init__(self):
        self.docsets = {}

        self.load_default_docsets()
        self.load_user_docsets()
        self.results_mappers = [
            VercelMapper(),
            TerraformMapper(),
            PrismaMapper(),
            WebDevMapper()
        ]

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

    def get_docsets(self, filter_term):
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

    def get_docset_by_key(self, key):
        """ Returns the details from a docset with the specified key passed as argument """
        if key in self.docsets:
            return self.docsets[key]

        return None

    def search(self, docset_key, term):
        """ Searches a term on a specific docset and return the results """
        docset = self.get_docset_by_key(docset_key)

        if not docset:
            raise ValueError("The specified docset is not known")

        if "provider" not in docset:
            raise ValueError(
                "Your docset configuration is missing provider option")

        if docset["provider"] == DOCS_PROVIDER_ALGOLIA_DOCSEARCH:
            return self.search_on_aloglia(docset_key, docset, term)
        elif docset["provider"] == DOCS_PROVIDER_MKDOCS:
            return self.search_on_mkdocs(docset_key, docset, term)

        return []

    def search_on_aloglia(self, docset_key, docset, term):
        algolia_client = SearchClient.create(docset['algolia_application_id'],
                                             docset['algolia_api_key'])

        index = algolia_client.init_index(docset['algolia_index'])

        try:
            search_results = index.search(
                term, self.get_search_request_options_for_docset(docset))

            if not search_results['hits']:
                return []

            return self.map_results(docset_key, docset, search_results["hits"])
        except AlgoliaException as e:
            LOGGING.error("Error fetching documentation from algolia: %s", e)
            raise e

    def search_on_mkdocs(self, docset_key, docset, query):

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

    def get_results_mapper(self, docset_key):
        """
        Returns the mapper object that will map the specified docset data into the format required by the extension
        """
        for mapper in self.results_mappers:
            if mapper.get_type() == docset_key:
                return mapper

        return DefaultMapper()

    def map_results(self, docset_key, docset_data, results):
        """ Maps the results returned by Algolia Search """

        mapper = self.get_results_mapper(docset_key)
        items = []
        for hit in results:
            mapped_item = mapper.map(docset_data, hit)
            items.append(mapped_item)

        return items

    def get_search_request_options_for_docset(self, docset):
        """
        Allow to specify custom search options for a specific docset
        Parameters:
            docset (string): The identifier of the docset.
        """
        opts = {}

        if "facet_filters" in docset:
            opts = {"facetFilters": docset["facet_filters"]}

        return opts

    def get_docsets_by_provider(self, provider):
        items = {}
        for key, docset in self.docsets.items():
            if docset["provider"] == provider:
                items[key] = docset

        return items
