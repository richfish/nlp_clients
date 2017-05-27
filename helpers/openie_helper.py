# java server
# from ~/Downloads/stanford-corenlp-full-2016-10-31
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer

from pycorenlp import StanfordCoreNLP

class OpenIEHelper():
    def __init__(self, corpus=None):
        self.nlp = StanfordCoreNLP('http://localhost:9000')
        self.corpus = corpus
        self.raw_sents = []
        self.open_ie_sets = []

    def open_ie(self, corpus=None):
        if not corpus:
            corpus = self.corpus
        openie_sets = []; raw_sents = []        

        output = self.nlp.annotate(corpus, properties={'annotators': 'natlog,openie', 'outputFormat': 'json'})
        num_sents = output['sentences']
        for i in range(0, len(num_sents)):
            sent = output['sentences'][i]
            raw_sents.append(sent)
            openie_sets.append(sent['openie'])
        self.raw_sents = raw_sents
        self.open_ie_sets = openie_sets
