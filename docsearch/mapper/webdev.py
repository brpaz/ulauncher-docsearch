from .default import DefaultMapper

import re


class WebDevMapper(DefaultMapper):
    """ Mapper for Terraform response """

    def get_type(self):
        return 'webdev'

    def map(self, docset, hit):
        """
        Map function converts an item returned from the Algolia DocSearch to the format to be rendered in Ulauncher
        """
        title = hit["_highlightResult"]["title"]["value"]

        url = "{}{}".format(docset["url"], hit["url"])

        return {
            'url': url,
            'title': self.remove_html(title),
            'icon': docset['icon'],
            'category': url
        }

    def remove_html(self, text):
        regex = re.compile(r'<[^>]+>')
        return regex.sub('', text)
