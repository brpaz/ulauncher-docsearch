import logging

from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from docsearch.listeners.query_listener import KeywordQueryEventListener
from docsearch.searcher import Searcher
from threading import Thread, Timer
from docsearch.indexers.mkdocs import MkDocsIndexer
from docsearch.searcher import DOCS_PROVIDER_MKDOCS

logger = logging.getLogger(__name__)

MKDOCS_INDEXER_INTERVAL = 7200


class DocsearchExtension(Extension):
    """ Main Extension Class  """

    def __init__(self):
        """ Extension constructor"""
        super(DocsearchExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.searcher = Searcher()
        self.mkdocs_indexer = MkDocsIndexer()

        th = Thread(target=self.index_mkdocs)
        th.daemon = True
        th.start()

    def index_mkdocs(self):

        docsets_to_index = self.searcher.get_docsets_by_provider(
            DOCS_PROVIDER_MKDOCS)

        for key, doc in docsets_to_index.items():
            try:
                logger.info("Indexing mkdocs docset for %s", key)
                self.mkdocs_indexer.index(key, doc)
            except Exception as e:
                logger.error("Error indexing mkdocs index for %s. Error: %s",
                             key, e)

        timer = Timer(MKDOCS_INDEXER_INTERVAL, self.index_mkdocs)
        timer.daemon = True
        timer.start()

    def list_docsets(self, event, query):
        """ Displays a list of available docs """

        docs = self.searcher.get_docsets(query)

        items = []

        if not docs:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name='No docsets found matching your criteria',
                    on_enter=HideWindowAction())
            ])

        for doc in docs[:8]:
            items.append(
                ExtensionResultItem(
                    icon=doc['icon'],
                    name=doc['name'],
                    description=doc['description'],
                    on_alt_enter=OpenUrlAction(doc['url']),
                    on_enter=SetUserQueryAction(
                        "%s %s " % (event.get_keyword(), doc['key']))))

        return RenderResultListAction(items)

    def search_in_docset(self, docset, query):
        """ Show documentation for a specific Docset """
        if len(query.strip()) < 3:
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                                    name='Please keep typing ...',
                                    description='searching %s documentation' %
                                    docset,
                                    highlightable=False,
                                    on_enter=HideWindowAction())
            ])

        results = []

        try:
            results = self.searcher.search(docset, query)
        except Exception as e:
            logger.error(e)
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name='An error occurred fetching documentation',
                    description=str(e),
                    highlightable=False,
                    on_enter=HideWindowAction())
            ])

        items = []

        if not results:
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                                    name='No results matching your criteria',
                                    highlightable=False,
                                    on_enter=HideWindowAction())
            ])

        for result in results[:8]:
            items.append(
                ExtensionResultItem(icon=result['icon'],
                                    name=result['title'],
                                    description=result['category'],
                                    highlightable=False,
                                    on_enter=OpenUrlAction(result['url'])))

        return RenderResultListAction(items)
