class BaseProvider(object):

    def get_name(self):
        raise NotImplementedError()

    def search(self, docset_key, docset, term):
        raise NotImplementedError()


class SearchException(Exception):
    pass
