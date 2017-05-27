# Semantic Affordance Dataset

import scipy.io
import re
from os import listdir
from os.path import isfile, join
from pprint import pprint as pp

class Affordances():
    def __init__(self):
        self.dir_path = "../assets/affordance_data/"
        filen_list = [f for f in listdir(self.dir_path) if isfile(join(self.dir_path, f))]
        pat = re.compile("\d{2}_")
        self.filen_list = [x for x in filen_list if pat.match(x)]

    def get_sets_and_frames(self):
        self.all_sets = self.get_all_data_sets_from_files()
        self.all_high_valence_pairs = filter(lambda x: x[-1] >= 4, self.all_sets)
        self.rel_y_frames_hv = list(set(self.make_rel_y_frames_hv())) #15k
        return self.rel_y_frames_hv

    def get_all_data_sets_from_files(self):
        all_sets = []
        for filen in self.filen_list:
            print(filen)
            parsedf = scipy.io.loadmat(self.dir_path + filen)
            np_arr = [x[0] for x in parsedf['data']]
            for numpy_obj in np_arr:
                vpos = numpy_obj[0][0][0][0][0][0]
                vword = numpy_obj[0][0][0][1][0]
                # if len(numpy_obj[1][0][0][0]) == 0:
                #     npos = 'n'
                # else:
                #     npos = numpy_obj[1][0][0][0][0][0]
                npos = 'n'
                nword = numpy_obj[1][0][0][1][0]
                score = numpy_obj[2][0][0]
                all_sets.append([vpos, vword, npos, nword, score])
        return all_sets

    def make_rel_y_frames_hv(self):
        frames = []
        for pair in self.all_high_valence_pairs:
            frame = "<rel {}><Y {}>".format(pair[1], pair[3])
            frames.append(frame)
        return frames



# raw = scipy.io.loadmat("../assets/affordance_data/01_person.mat")
#
#
# Affordances are fundamental attributes of objects. Affordances
# reveal the functionalities of objects and the possible
# actions that can be performed on them. Understanding affordances
# is crucial for recognizing human activities in visual
# data and for robots to interact with the world. In this
# paper we introduce the new problem of mining the knowledge
# of semantic affordance: given an object, determining
# whether an action can be performed on it. This is equivalent
# to connecting verb nodes and noun nodes in WordNet,
# or filling an affordance matrix encoding the plausibility
# of each action-object pair
#
#
# Semantic Affordance Dataset
#
# Author:   Yu-Wei Chao
# Updated:  06/15/2015
#
# ==============================================================================
# Information
# ==============================================================================
# The folder semantic_affordance_data/ contains following items:
#
# 1. affordance labels for 91 MS-COCO object categories
#
#   Each file ${MS-COCO id}_${object name}.mat contains a struct array 'data'
#   with the following fields:
#
#     a. verb_syn:  Verb synsets from WordNet.
#
#       'id':    synset id, which is the concatenation of POS (i.e. part of
#                speech) and SYNSET OFFSET of WordNet
#       'name':  synset name
#       'def':   synset definition
#       'exam':  one example sentence from the synset
#
#       'adef1','adef2','adef3' are alternative definitions of the word in
#       'name', which are only used for collecting annotations.
#
#     b. noun_syn:  Noun synsets from WordNet.
#
#     c. score:  Plausibility score for the vn-pair, ranging from 1 to 5.
#
#        5: Definitely Yes
#        4: Normally Yes
#        3: Maybe
#        2: Normally No
#        1: Definitely No/Make No Sense
#
#        This score is averaged over 5 different annotators.
#
#     d. raw_anno:  Raw annotations from the 5 annotators.
#
#        1: Definitely Yes
#        2: Normally Yes
#        3: Maybe
#        4: Normally No
#        5: Definitely No
#        6: Make No Sense
#        7: Don't Know
#
# 2. mcoco.mat
#
#   Metadata of the MS-COCO object categories.
#
# 3. verb_syn_visualness.mat
#
#   Visualness scores for the selected 2375 verb synsets. Structure is similar
#   to affordance label files.
