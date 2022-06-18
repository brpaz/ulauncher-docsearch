"""
Module responsible for search into docs
"""

import json
import os
import logging

from docsearch.providers.constants import PROVIDER_MKDOCS, PROVIDER_ALGOLIA_DOCSEARCH
from docsearch.providers.factory import ProviderFactory

DEFAULT_DOC_IMAGE = 'images/icon.png'

LOGGING = logging.getLogger(__name__)

DOCSETS_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data',
                                 'docsets.json')

USER_DOCSETS_PATH = os.path.join(os.path.expanduser("~"), ".config",
                                 "ulauncher", "ext_preferences", "docsearch")


class Searcher:
    """ Class that handles the documentation search """

    def __init__(self):
        self.docsets = {}

        self.load_default_docsets()
        self.load_user_docsets()
        self.provider_factory = ProviderFactory()

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

        provider = self.provider_factory.get(docset["provider"])

        return provider.search(docset_key, docset, term)

    def get_docsets_by_provider(self, provider):
        items = {}
        for key, docset in self.docsets.items():
            if docset["provider"] == provider:
                items[key] = docset

        return items
