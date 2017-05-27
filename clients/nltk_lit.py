from collections import defaultdict
import re
import nltk
from nltk.corpus import gutenberg

from helpers.spacy_helper import SpacyHelper

# remove ole english, poetry, bible
# ['bible-kjv.txt', 'blake-poems.txt', 'whitman-leaves.txt', 'shakespeare-macbeth.txt',
#    'milton-paradise.txt', 'shakespeare-caesar.txt', 'shakespeare-hamlet.txt']


class NltkLitMiner():
    def __init__(self):
        self.spacyh = SpacyHelper()
        #self.jane_austen_sents = self.filter_short_basic('austen-emma.txt', 'austen-persuasion.txt', 'austen-sense.txt')
        self.chesterton_sents = self.filter_short_strong('chesterton-ball.txt', 'chesterton-brown.txt', 'chesterton-thursday.txt')
        # self.chesterton_noun_phrases = self.get_nphrase_chunks('chesterton-thursday.txt')
        # self.chesterton_short_sents_basic = self.filter_short_basic('chesterton-ball.txt', 'chesterton-brown.txt', 'chesterton-thursday.txt')
        # etc...

    fileids_to_use = [
        'austen-emma.txt',
        'austen-persuasion.txt',
        'austen-sense.txt',
        'bryant-stories.txt',
        'burgess-busterbrown.txt',
        'carroll-alice.txt',
        'chesterton-ball.txt',
        'chesterton-brown.txt',
        'chesterton-thursday.txt',
        'edgeworth-parents.txt',
        'melville-moby_dick.txt'
    ]

    def get_words_for_file(self, fileid):
        return gutenberg.words(fileid)

    def get_raw_for_file(self, fileid):
        return gutenberg.raw(fileid)

    def get_sents_for_file(self, fileid):
        return gutenberg.sents(fileid)

    def retrieve_short_sents(self, fileid):
        sents_raw = self.get_sents_for_file(fileid)
        #sents = self.spacy_sents(fileid)
        return [sent for sent in sents_raw if 3 < len(sent) < 11]

    def split_sents_with_conjunctions(self):
        pass

    def filter_short_basic(self, *fileids):
        all_sents = []
        for fileid in fileids:
            short_sents = self.retrieve_short_sents(fileid)
            for sent in short_sents:
                sent_lower = [x.lower() for x in sent]
                if "?" in sent_lower or "\"" in sent_lower or "chapter" in sent_lower:
                    continue
                all_sents.append(sent)
        print("num sents basic filtering for", fileids, len(all_sents))
        return all_sents

    def filter_short_strong(self, *fileids):
        sents = self.filter_short_basic(fileids)
        filtered = []
        for sent in sents:
            sent = " ".join(sent)
            parsed_s = self.spacyh.parse(sent)
            if self.spacyh.is_proper_sentence(parsed_s):
                filtered.append(sent)
        print("num sents Spacy proper sent filtering", fileids, len(filtered))
        return filtered


    def get_nphrase_chunks(self, *fileids):
        n_chunks = []
        for fileid in fileids:
            sents_raw = gutenberg.sents(fileid)
            for sent in sents_raw:
                sent = " ".join(sent)
                parsed_s = self.spacyh.parse(sent)
                chunks = self.spacyh.get_nphrase_chunks(parsed_s)
                n_chunks.extend(chunks)
        return n_chunks
