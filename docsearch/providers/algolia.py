import logging
from typing import List
from .base import BaseProvider
from .constants import PROVIDER_ALGOLIA_DOCSEARCH
from .base import SearchException
from docsearch.mapper import DefaultMapper, VercelMapper, PrismaMapper, TerraformMapper, WebDevMapper
from algoliasearch.search_client import SearchClient
from algoliasearch.exceptions import AlgoliaException

logger = logging.getLogger(__name__)


class AlgoliaProvider(BaseProvider):

    def __init__(self):
        self.result_mappers: List = [
            VercelMapper(),
            TerraformMapper(),
            PrismaMapper(),
            WebDevMapper()
        ]

    def get_name(self):
        return PROVIDER_ALGOLIA_DOCSEARCH

    def search(self, docset_key, docset, term):
        algolia_client = SearchClient.create(docset['algolia_application_id'],
                                             docset['algolia_api_key'])

        index = algolia_client.init_index(docset['algolia_index'])

        try:
            search_results = index.search(term,
                                          self.build_request_options(docset))

            if not search_results['hits']:
                return []

            return self.map_results(docset_key, docset, search_results["hits"])
        except AlgoliaException as e:
            logger.error("Error fetching documentation from algolia: %s", e)
            raise SearchException(
                "Error fetching documentation from algolia: %s", e)

    def build_request_options(self, docset):
        """
        Allow to specify custom search options for a specific docset
        Parameters:
            docset (string): The identifier of the docset.
        """
        opts = {}

        if "facet_filters" in docset:
            opts = {"facetFilters": docset["facet_filters"]}

        return opts

    def get_results_mapper(self, docset_key):
        """
        Returns the mapper object that will map the specified docset data into the format required by the extension
        """
        for mapper in self.result_mappers:
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
