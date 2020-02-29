"""
Doc search extension
This extension provides full text search on popular documentation sites, powered by Algolia.
"""
import logging

# pylint: disable=import-error
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from docs import DocSearch

LOGGING = logging.getLogger(__name__)


class DocsearchExtension(Extension):
    """ Main Extension Class  """
    def __init__(self):
        """ Extension constructor"""
        super(DocsearchExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.searcher = DocSearch()

    def show_available_docs(self, event, filter_term=None):
        """ Displays a list of available docs """
        docs = self.searcher.get_available_docs(filter_term)

        items = []

        if not docs:
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                                    name='No results found',
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
                        "%s %s > " % (event.get_keyword(), doc['key']))))

        return RenderResultListAction(items)


class KeywordQueryEventListener(EventListener):
    """ Listener that handles the user input """

    # pylint: disable=unused-argument,no-self-use
    def on_event(self, event, extension):
        """ Handles the event """

        arg = event.get_argument() or ""

        args_array = arg.split(">")
        if len(args_array) != 2:
            return extension.show_available_docs(event, arg)

        try:

            docset = args_array[0].strip()

            search_term = args_array[1]

            if len(search_term.strip()) < 3:
                return RenderResultListAction([
                    ExtensionResultItem(
                        icon='images/icon.png',
                        name='Please type a minimum of 3 characters',
                        description='Searching ...',
                        on_enter=HideWindowAction())
                ])

            result = extension.searcher.search(docset, search_term)

            items = []

            if not result:
                return RenderResultListAction([
                    ExtensionResultItem(
                        icon='images/icon.png',
                        name='No results matching your criteria',
                        on_enter=HideWindowAction())
                ])

            for i in result[:8]:
                items.append(
                    ExtensionResultItem(icon=i['icon'],
                                        name=i['title'],
                                        description=i['category'],
                                        highlightable=False,
                                        on_enter=OpenUrlAction(i['url'])))

            return RenderResultListAction(items)

        except Exception as err:
            raise err
            # return RenderResultListAction([
            #     ExtensionResultItem(
            #         icon="images/icon.png",
            #         name='An error ocurred when searching documentation',
            #         description='err',
            #         on_enter=HideWindowAction()
            #     )
            # ])


if __name__ == '__main__':
    DocsearchExtension().run()
