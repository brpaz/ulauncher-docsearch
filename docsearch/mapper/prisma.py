from .default import DefaultMapper


class PrismaMapper(DefaultMapper):
    """ Mapper for Algolia Docsearch response for Prisma documentation """

    def get_type(self):
        return 'prisma'

    def map(self, docset, hit):
        """
        Map function converts an item returned from the Algolia DocSearch to the format to be rendered in Ulauncher
        """

        title = hit["title"]
        description = hit["content"]
        url = docset["url"] + hit['slug']

        return {
            'url': url,
            'title': title,
            'icon': docset['icon'],
            'category': description
        }
