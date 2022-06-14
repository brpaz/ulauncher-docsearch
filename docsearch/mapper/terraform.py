from .default import DefaultMapper


class TerraformMapper(DefaultMapper):
    """ Mapper for Terraform response """

    def get_type(self):
        return 'terraform'

    def map(self, docset, hit):
        """
        Map function converts an item returned from the Algolia DocSearch to the format to be rendered in Ulauncher
        """
        title = hit["page_title"]
        description = " -> ".join(hit["headings"])

        url = "{}/{}".format(docset["url"], hit["objectID"])

        return {
            'url': url,
            'title': title,
            'icon': docset['icon'],
            'category': description
        }
