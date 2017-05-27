# Get all valid entailments data from SNLI corpus

import pandas as pd
import csv
import random
import numpy as np


class Entailment():

    def __init__(self):
        df = pd.read_csv('../assets/snli_1.0/snli_1.0_dev.txt', sep="\t")
        df = df[['gold_label', 'sentence1', 'sentence2']]
        dfa = df[df.gold_label == "entailment"]

        df3 = pd.read_csv('../assets/snli_1.0/snli_1.0_test.txt', sep="\t")
        df3 = df3[['gold_label', 'sentence1', 'sentence2']]
        df3a = df3[df3.gold_label == "entailment"]

        df2 = pd.read_csv('../assets/snli_1.0/snli_1.0_train.txt', sep="\t")
        df2 = df2[['gold_label', 'sentence1', 'sentence2']]
        df2a = df2[df2.gold_label == "entailment"]

        self.original_data = pd.concat([df, df2, df3], axis=0)
        self.e_data = pd.concat([dfa, df2a, df3a], axis=0) # len 190k
        self.test_set1 = self.e_data.sentence1.values.tolist()[:60000]
        self.test_set2 = self.e_data.sentence2.values.tolist()[:60000]

    def parse_data_using_glove(self, test=True):
        pass

    # def glove2dict(self, src_filename):
    #     reader = csv.reader(open(src_filename), delimiter=' ', quoting=csv.QUOTE_NONE)
    #     return {line[0]: np.array(list(map(float, line[1: ]))) for line in reader}
    # glove = glove2dict("../assets/glove.6B/glove.6B.50d.txt")
