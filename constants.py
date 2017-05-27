ASSETS = "./assets/"

PRONOUNS = set(['it', 'he', 'she', 'they', 'them', 'his', 'her', 'him', 'himself', 'herself', 'themselves'])

# expand
PARSE_GUIDE_RULES = {
    'explanation': {
        "For -> Because",
        "But -> Because",
        "When -> Because"
    }
}

PS_BASIC_THRESHOLD = 0.1 #0-1, .1 + probably good
LCH_THRESHOLD = 0
WUP_THRESHOLD = 0
RES_THRESHOLD = 0
JCN_THRESHOLD = 0
LIN_THRESHOLD = 0

# mainly positional preps
KEEP_WORDS = ["because", "under", "around", "to", "through", "between", "behind", "against", "below", "before",
            "after", "here", "only", "up", "down", "left", "right", "out", "in", "into", "of", "during", "not", "nor", "neither", "while", "until",
            "some", "many", "now", "is", "are", "was", "be", "that", "and", "or"]
KEEP_WORDS2 = ["because", "under", "around", "through", "between", "against", "below", "here", "only", "up",
                "down", "left", "right"]
MORE_STOPS_GENERIC = ["seem", "said", "instead", "would"] # expand

#sub/ cord/ constrastive/ concessive conj words
