
import nltk
from nltk.corpus import wordnet as wn
from spacy_helper import SpacyHelper

class WnExamples():
    def __init__(self, parser):
        self.spacyh = SpacyHelper()
        self.parsed_examples = self.get_examples_parsed() #48,247
        self.parsed_examples_short = filter(lambda x: len(str(x)) < 50, self.parsed_examples) #39,982
        self.proper_sents = self.spacyh.get_proper_sents(self.parsed_examples_short)
        self.partial_phrases = self.spacyh.get_partial_phrases(self.parsed_examples_short)
        self.x_rel_frames = self.convert_to_x_rel_frames()

    def get_examples_parsed(self):
        raw = [x.examples() for x in wn.all_synsets()]
        raw2 = [y for x in raw for y in x]
        return map(lambda x: self.parser(x), raw2)

    def substitute_ner_labels(self, sent):
        after_sub = []
        entities = sent.ents
        for token in sent:
            if token in entities:
                label = self.ner_labels[token.ent_type_]
                after_sub.append(label)
            else:
                after_sub.append(token)
        return after_sub

    def convert_to_rel_y_frames(self):
        pass

    def convert_to_x_rel_frames(self):
        frames = []
        for sent in self.proper_sents:
            np = self.get_nsubj_phrase(sent)
            rest_sent = filter(lambda x: x not in np, sent)
            np = " ".join([x.text for x in np]).replace(".", "").strip()
            rest_sent = " ".join([x.text for x in rest_sent]).replace(".", "").strip()
            frame = "<X {}><rel {}>".format(np, rest_sent)
            frames.append(frame)
        return frames

    def convert_to_dependency_arr(self, token):
        pass
        #dep_labels = []
        # while token.head is not token:
        #     dep_labels.append(token.dep)
        #     token = token.head
        # return dep_labels
