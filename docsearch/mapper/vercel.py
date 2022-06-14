from .default import DefaultMapper


class VercelMapper(DefaultMapper):
    """  Mapper for the Vercel documentation """

    def get_type(self):
        return 'vercel'

    def map(self, docset, hit):
        """
        Map function converts an item returned from the Algolia DocSearch to the format to be rendered in Ulauncher
        """
        print(hit)
        url = docset["url"] + hit['url']

        description = hit['section']

        return {
            'url': url,
            'title': hit["title"],
            'icon': docset['icon'],
            'category': description
        }
