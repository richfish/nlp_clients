from clients.framenet import FramenetMiner

class FramenetHelper():
    def __init__(self):
        self.framenets = FramenetMiner().all_templates #1200/ #13k lus
        self.lus_by_frame = self.lus_by_frame() # same index as self.framenets

    def framenet_name_per_lu(self, word, pos=None):
        candidate_frame_names = []
        for frame in self.framenets:
            words = [x[0] for x in frame['lus']]
            if word in words:
                if pos:
                    if pos == word[1]:
                        candidate_frame_names.append(frame['f_name'])
                else:
                    candidate_frame_names.append(frame['f_name'])
        return candidate_frame_names

    def other_lus_in_frame_per_lu(self, word, pos=None):
        lu_candidate_sets = []
        lu_sets = [x['lus'] for x in self.framenets]
        for lu_set in lu_sets:
            words = [x[0] for x in lu_set]
            if word in words:
                if pos:
                    # better fix
                    if pos == word[1]:
                        lu_candidate_sets.append(word[0])
                else:
                    lu_candidate_sets.append(words)
        return lu_candidate_sets

    def core_roles_per_frame(self, frame):
        pass

    def parent_frames_for_frame(self, frame):
        pass
        # would be good to get top level frame list
          # or list of frames that are pointlessly abstract

    def lus_by_frame(self):
        lus_per_frame = []
        for frame in self.framenets:
            lus = frame['lus']
            flat = [x[0] for x in lus]
            lus_per_frame.append(flat)
        return lus_per_frame


# May need to coordinate Morphy, or stemming, for lu matching also

# Note a lexunit search has collocation overlap

# maybe POS more granularity; assumes word already in form/ base etc.
# ['A', 'ADV', 'C', 'ART', 'SCON', 'V', 'N', 'PRON', 'NUM', 'IDIO', 'INTJ', 'PREP']

# probably only want to check frames for common nouns and verbs
  # To avoid having to parse, can just use stop words heuristics
  # Can do a more basic, lighteweight Spacy parse??
