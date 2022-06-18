from typing import List
from .base import BaseProvider
from .algolia import AlgoliaProvider
from .mkdocs import MkDocsProvider


class ProviderFactory(object):

    def __init__(self):
        self.providers: List[BaseProvider] = [
            MkDocsProvider(), AlgoliaProvider()
        ]

    def get(self, name: str) -> BaseProvider:
        for provider in self.providers:
            if provider.get_name() == name:
                return provider

        raise RuntimeError("Provider with name '%s' was not found" % name)
