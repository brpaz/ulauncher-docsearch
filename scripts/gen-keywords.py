""" This script parses the docsets and generates a list of keywords for each specific docset """

import os
import json


def gen_keywords():

    docsets_file = os.path.join(os.path.dirname(__file__), '..', 'data',
                                'docsets.json')

    # manifest_file = os.path.join(os.path.dirname(__file__), '..',
    #                              'manifest.json')
    docsets = {}
    with open(docsets_file, 'r') as data:
        docsets = json.load(data)

    keywords = []
    for key in docsets:
        docset = docsets[key]
        keywords.append({
            "id": "kw_%s" % key,
            "type": "keyword",
            "name": "%s Documentation" % docset["name"],
            "default_value": "docs:%s" % key,
            "icon": docset["icon"]
        })

    docs_kws = json.dumps(keywords, indent=4)
    print(docs_kws)
    # with open(manifest_file, 'r') as data:
    #     manifest = json.load(data)
    #     merged_prefs = manifest["preferences"] + docs_kws
    #     print(merged_prefs)


if __name__ == '__main__':
    gen_keywords()
