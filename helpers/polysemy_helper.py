from nltk.corpus import wordnet as wn
from nltk.corpus import framenet as fn
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
#Snowball stemmer? quickist
import constants
import pdb

class PolysemyHelper():

    def __init__(self):
        self.stopwords = stopwords.words('english')

    def calculate_congruency_score_arr_vs_arr(self, arr1, arr2):
        arr1 = self.clean_word_arr(arr1)
        arr2 = self.clean_word_arr(arr2)
        score = 0
        for word in arr1:
            for word2 in arr2:
                if self.match_by_exact(word, word2):
                    score += 2
                elif self.match_by_wc(word, word2):
                    score += 1
        print("POLYSEMY CONGRUENCY SCORE... arr1: {} | arr2: {} | score: {}".format(arr1, arr2, score))
        return score

    def match_by_exact(self, term1, term2):
        if term1 == term2:
            return True
        stemmer1 = PorterStemmer()
        if stemmer1.stem(term1) == stemmer1.stem(term2):
            return True
        stemmer2 = LancasterStemmer()
        stem2a = stemmer2.stem(term1)
        stem2b = stemmer2.stem(term2)
        if stem2a == stem2b:
            return True
        return False

    def match_by_exact_no_stemming(self, term1, term2):
        if term1 == term2:
            return True

    def match_by_exact_with_morphy(self, term1, term2):
        if term1 == term2:
            return True
        #if wn.morphy(term1) == wn.morphy(term2):
        #    return True

    def match_by_wc(self, term1, term2):
        #additional strategies than WN could be used here
        wc_term1 = self.__basic_wn_cloud(term1)
        wc_term2 = self.__basic_wn_cloud(term2)
        for lemma in wc_term1:
            if lemma in wc_term2:
                return True
        return False

    def match_by_hypernym(self, term1, term2):
        hypernym_list_1 = self.hypernym_list(term1)
        hypernym_list_2 = self.hypernym_list(term2)
        for hypernym in hypernym_list_1:
            if hypernym in hypernym_list_2:
                return True
        return False

    # NEW could do hypernym where abstract up to nth - top level
    # top levle is too abstract, but some offset below might be good

    def hypernym_list(self, word):
        hypernyms = [x.hypernyms() for x in wn.synsets(word)]
        return [y for x in hypernyms for y in x]

    def match_by_fn_frames(self, term2, term1):
        fn_names1 = __framenet_name_list
        fn_names2 = __framenet_name_list
        for name in fn_names1:
            if name in fn_names2:
                return True
        return False

    def __fn_names_list(self, term):
        names = [x.name for x in fn.frames_by_lemma(r'')]
        return [x.lower().replace("_", "") for x in names]


    def match_by_dictionary_api_bow(self, term1, term2):
        pass

    def __get_dictionary_bow(self, term, num_dictionaries='all'):
        pass

    def match_by_wikipedia_bow(self, term1, term2):
        pass

    def __get_wikipedia_bow(self, term):
        pass

    def reddit_similarity_score(self, term):
        pass

    def self_frame_lookup(self, term):
        pass


    def match_by_path_similarity_score(self, term1, term2, pos1=None, pos2=None):
        synset1 = ""
        synset2 = ""
        basic_similarity = synset1.path_similarity(synset2) > constants.PS_BASIC_THRESHOLD
        # lch_similarity = sysnset1.lch_similarity(synset2) > constants.LCH_THRESHOLD
        # wup_similarity = sysnset1.wup_similarity(synset2) > constants.WUP_THRESHOLD
        # res_similarity = sysnset1.res_similarity(synset2) > constants.RES_THRESHOLD
        # jcn_similarity = sysnset1.jcn_similarity(synset2) > constants.JCN_THRESHOLD
        # lin_similarity = sysnset1.lin_similarity(synset2) > constants.LIN_THRESHOLD

    def match_by_entailment(self):
        pass

    def match_by_meronym(self):
        pass

    def match_by_holonym(self):
        #.part_holonyms for the 'whole' that the thing is a part of
        pass

    def __basic_wn_cloud(self, word):
        lemmas = [x.lemma_names() for x in wn.synsets(word)]
        return [y for x in lemmas for y in x]

    def __basic_wn_cloud_squared(self, word):
        lemma_sets = [_basic_wn_cloud(word) for word in self.__basic_wn_cloud]
        return [y for x in lemma_sets for y in x]

    def clean_word_arr(self, word_arr, keep_words=None, ok=False): #assumes list of tokens I guess
        original_word_arr = list(word_arr)
        if not self.__all_words_stop_words(word_arr): #special case, simple but important phrases like 'but he was not there', just keep all if stopwords remove all
          word_arr = self.__remove_stop_words_from_phrase(word_arr)
        cleaner_word_arr = filter(lambda x: x not in constants.IGNORE_WORDS, word_arr)
        if keep_words:
            for word in keep_words:
                if (word in original_word_arr) and (word not in cleaner_word_arr):
                    cleaner_word_arr.append(word)
        return cleaner_word_arr


    #maybe get rid of this
    def back_to_tokens(self, phrase):
        if not self.__all_words_stop_words(phrase): #special case, simple but important phrases like 'but he was not there', just keep all if stopwords remove all
          phrase = self.__remove_stop_words_from_phrase(phrase)
        return filter(lambda x: x not in constants.IGNORE_WORDS, phrase)

    def __remove_stop_words_from_phrase(self, phrase):
        #requires flat arr
        core_words = []
        if type(phrase) is str:
          phrase = phrase.split(" ")
        for word in phrase:
             if not word in self.stopwords:
                 core_words.append(word)
        if len(core_words) == len(phrase):
            return phrase
        return core_words

    def __all_words_stop_words(self, phrase):
        if type(phrase) is str:
            phrase = phrase.split(" ")
        filtered_phrase = filter(lambda x: x in self.stopwords, phrase)
        if filtered_phrase == phrase:
            return True

    #http://stackoverflow.com/questions/15730473/wordnet-find-synonyms
    #go through all synsets looking for reasonably related words
    def syn(word, lch_threshold=2.26):
        for net1 in wn.synsets(word):
            for net2 in wn.all_synsets():
                try:
                    lch = net1.lch_similarity(net2)
                except:
                    continue
                # The value to compare the LCH to was found empirically.
                # (The value is very application dependent. Experiment!)
                if lch >= lch_threshold:
                    yield (net1, net2, lch)





#OLD methods

# def wn_has_synset_cloud_check(word, pos=None):
#     cloud_raw = wn.synsets(word)
#     if not cloud_raw:
#         return False
#     else:
#         return True
#
# def wn_synset_first_match(word, pos=None):
#     cloud_raw = wn.synsets(word)
#     return [str(x) for x in cloud_raw[0].lemma_names()]
#
# def wn_synset_cloud_similar_words(word, pos=None):
#     if pos:
#       pos_wn_maprinter = {}
#       pos = pos_wn_maprinter[pos]
#     synset = wn.synset("{}.{}.01".format(word, pos))
#     cloud_raw = synset.similar_tos()
#     return set([str(y) for x in names_raw for y in x])
#
# def wn_synset_cloud_basic(word, pos=None):
#     cloud_raw = wn.synsets(word)
#     names_raw = [x.lemma_names() for x in cloud_raw]
#     return set([str(y) for x in names_raw for y in x]) #flattened arr of synonym names
#
# def framenet_lu_cloud(word, pos=None):
#     #not sure how usefull
#     return [x.lexemes[0].name for x in fn.lus(word)]
