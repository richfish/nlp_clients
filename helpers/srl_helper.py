from practnlptools.tools import Annotator
import nltk
wnl = nltk.WordNetLemmatizer()

class SRLHelper():
    def __init__(self):
        self.annotator = Annotator()

    def get_annotations_for_sent(self, sent, dep_parse=False):
        return self.annotator.getAnnotations(sent, dep_parse=dep_parse)

    def get_verbs(self, sent):
        vs = self.get_annotations_for_sent(sent)['verbs']
        return [wnl.lemmatize(x.lower(), 'v') for x in vs] #replacement for morphy

    def get_predicates(self, sent):
        self.get_verbs(sent)
    # propbank roles
    def get_srl(self, sent):
        return self.get_annotations_for_sent(sent)['srl']
