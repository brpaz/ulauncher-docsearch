from ulauncher.api.client.EventListener import EventListener


class KeywordQueryEventListener(EventListener):
    """ Listener that handles the user input """

    # pylint: disable=unused-argument,no-self-use
    def on_event(self, event, extension):
        """ Handles the event """

        query = event.get_argument() or ""

        kw_docset = extension.get_docset_from_keyword(event.get_keyword())
        if kw_docset:
            return extension.search_in_docset(kw_docset, query)

        query_parts = query.split(" ")
        docset = query_parts[0].strip()

        if extension.searcher.has_docset(docset):
            term = " ".join(query_parts[1:])
            return extension.search_in_docset(docset, term)

        return extension.list_docsets(event, query)
