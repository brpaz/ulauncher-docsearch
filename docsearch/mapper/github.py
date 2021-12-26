from .default import DefaultMapper


class GitHubMapper(DefaultMapper):
    """  Mapper for the GitHub documentation """
    def map(self, docset, hit):
        """
        Map function converts an item returned from the Algolia DocSearch to the format to be rendered in Ulauncher
        """
        title = hit["heading"]
        description = hit["breadcrumbs"]
        url = hit["url"]

        return {
            'url': url,
            'title': title,
            'icon': docset['icon'],
            'category': description
        }
