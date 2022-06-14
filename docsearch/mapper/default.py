""" Default mapper for Algoia Docsearch responses """


class DefaultMapper():

    def get_type(self):
        return "default"

    def map(self, docset, hit):

        print(hit)
        title, description = self.map_description(hit)

        if not description:
            description = hit['url']

        return {
            'url': hit['url'],
            'title': title,
            'icon': docset['icon'],
            'category': description
        }

    def map_description(self, hit):
        """ Returns the text to display as result item title """
        hierarchy = hit['hierarchy'].values()

        # Filter the list by removing the empty values
        res = [i for i in hierarchy if i]

        if len(res) < 2:
            return res[0], ""

        # The last element found will be the description and the previous one the title.
        return res[-1], ' -> '.join(res[:-1])
