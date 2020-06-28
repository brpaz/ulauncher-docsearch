"""
Doc search extension
This extension provides full text search on popular documentation sites, powered by Algolia.
"""
import logging

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from docsearch.searcher import Searcher

logger = logging.getLogger(__name__)


class DocsearchExtension(Extension):
    """ Main Extension Class  """
    def __init__(self):
        """ Extension constructor"""
        super(DocsearchExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.searcher = Searcher()

    def show_docsets_list(self, event, query):
        """ Displays a list of available docs """

        docs = self.searcher.get_available_docs(query)

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

    def show_docs_for_docset(self, docset, query):
        """ Show documentation for a specific Docset """
        if len(query.strip()) < 3:
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                                    name='please keep typing ...',
                                    description='searching %s documentation' %
                                    docset,
                                    highlightable=False,
                                    on_enter=HideWindowAction())
            ])

        results = self.searcher.search(docset, query)

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

    def get_docset_from_keyword(self, keyword):
        """ Returns a docset matching the extension keyword or None if no matches found """
        kw_id = None
        for key, value in self.preferences.items():
            if value == keyword:
                kw_id = key
                break

        if kw_id:
            kw_parts = kw_id.split("_")
            if len(kw_parts) == 2 and kw_parts[0] == "kw":
                return kw_parts[1]

        return None


class KeywordQueryEventListener(EventListener):
    """ Listener that handles the user input """

    # pylint: disable=unused-argument,no-self-use
    def on_event(self, event, extension):
        """ Handles the event """

        query = event.get_argument() or ""

        kw_docset = extension.get_docset_from_keyword(event.get_keyword())
        if kw_docset:
            return extension.show_docs_for_docset(kw_docset, query)

        query_parts = query.split(" ")
        docset = query_parts[0].strip()

        if extension.searcher.has_docset(docset):
            term = " ".join(query_parts[1:])
            return extension.show_docs_for_docset(docset, term)

        return extension.show_docsets_list(event, query)


if __name__ == '__main__':
    DocsearchExtension().run()
