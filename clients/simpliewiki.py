from collections import defaultdict
import re
from os import listdir
from os.path import isfile, join
from pprint import pprint as pp
import json
import xml.etree.ElementTree as ET

#from helpers.spacy_helper import SpacyHelper

class SimplewikiMiner():
    def __init__(self, pages=None):
        #self.spacyh = SpacyHelper()
        self.pages = pages
        if not pages:
            self.pages = ET.parse('../assets/simplewikibig.xml').getroot()
        #self.all_noun_phrases = [] #careful, could take an eternity with np parsing
        #self.all_short_sents = []
        self.content_article_name_pat = re.compile("\\'\\'\\'(.+?)\\'\\'\\'")
        self.content_wiki_link_pat = re.compile("\[\[(.+?)\]\]")
        self.content_double_list_pat = re.compile("[a-zA-Z0-9()]{1,20}(\|[a-zA-Z0-9()]{1,20})")
        self.content_heading_pat = re.compile("==.+?==")
        self.content_ref_tags_pat = re.compile("<ref .+?\/>")
        self.content_ref_tags2_pat = re.compile("<ref>.+<\/ref>")
        self.content_braces_tag_pat = re.compile("\{\{.+?\}\}")
        self.content_cat_tags_pat = re.compile("\[\[Category:.+?\]\]")

        self.all_page_nodes = self.build_all_nodes(self.pages) # ~118,000
        self.all_sents_raw = self.combine_all_sents()
        self.all_sents_better = []

    def pp_template(self, template):
        pp(json.loads(json.dumps(template)))

    def base_node(self):
        return defaultdict(str, {
            "title": "",
            "content": []
        })

    def build_node(self, page):
        node = self.base_node()
        node["title"] = page[0].text #may not always be right,  'title' in str([x for x in root[9000]][0]) --> might be time consuming
        node["content"] = self.cleanup_content(page[-1][-2].text)
        return node

    def build_all_nodes(self, all_pages=None):
        nodes = []
        #known_bad_pages = []#[35856, 59592, 59608] #beyonce, the X factor, breaking bc/ of regex
        for i, page in enumerate(all_pages):
            # if i in known_bad_pages:
            #     continue
            if self.should_include_page(page):
                nodes.append(self.build_node(page))
        print("number of nodes built", len(nodes))
        return nodes

    def should_include_page(self, page):
        bad_titles = ['category', 'wikipedia', 'mediawiki', 'template', 'list of']
        bad_content = ['#redirect']
        title_txt = page[0].text
        content_txt = page[-1][-2].text
        if title_txt is None or content_txt is None: # ~10.0 missing for no reason
            return False
        if filter(lambda x: x in title_txt.lower(), bad_titles): # ~50k internal/ category titles
            return False
        if filter(lambda x: x in content_txt.lower(), bad_content): # ~50k redirects
            return False
        if len(content_txt) < 140: # ~1.5k too short
            return False
        return True

    def combine_all_sents(self):
        combined = []
        for node in self.all_page_nodes:
            combined.append(node['content'])
        return combined

    def cleanup_content(self, content):
        splits = self.content_article_name_pat.split(content, 1)
        if len(splits) > 2:
          content = splits[1] + splits[2]
        content = re.sub(self.content_article_name_pat, r"\1", content)
        content = content.split("==References==")[0]
        content = content.replace("\n", " ")
        #removing weird file stuff in middle of article
        content = self.remove_weird_file_stuff_in_middle(content)
        #[[English language|English]] how to handle... delete one on right?
        matches = self.content_wiki_link_pat.findall(content)
        #for match in matches:
            #content = content.replace(match,'') #showing quirks, doing it this way
        #heading == Histroy of thing == maybe want to keep and use as keys??
        matches = self.content_heading_pat.findall(content)
        for match in matches:
            content = content.replace(match, '')
        #<ref name=''/> tags in a lot of articles
        matches = self.content_ref_tags_pat.findall(content)
        for match in matches:
            content = content.replace(match, '')
        return content
        #<ref>{{annoying content}}</ref> is a thing too
        matches = self.content_ref_tags2_pat.findall(content)
        for match in matches:
            content = content.replace(match, '')
        #{{ often random useless thing }}
        matches = self.content_braces_tag_pat.findall(content)
        for match in matches:
            content = content.replace(match, '')
        #remove category tags - may want to use in future
        matches = self.content_cat_tags_pat.findall(content)
        for match in matches:
            content = content.replace(match, '')
        #removing [[thing]] brackets, because Spacy NER is good...
        content = content.replace("[[", '').replace("]]", '')

        return content
        #Todo could probably speed this up by combining regexes into one?, instead of 8 different findall/sub calls

    def remove_weird_file_stuff_in_middle(self, content):
        start_i = content.find("{|")
        end_i = content.find("|}")
        both_match = (start_i != -1 and end_i != -1)
        if both_match and (start_i > end_i):
            content = content[:end_i] + content[end_i+2:]
            self.remove_weird_file_stuff_in_middle(content)
            return content
        if both_match:
            bad_str = content[start_i:end_i+2]
            content = content[:start_i] + content[end_i+2:]
            self.remove_weird_file_stuff_in_middle(content)
            return content
        else:
            return content
