# vs. auxiliary vs. collocations ...
# part of this is recognizing passive -- come under attack, be attacked, be thanked, etc.
# expand

class LightVerbHelper():
    def lvc_key_list(self):
        lvc = [
            "take",
            "have",
            "make",
            "give",
            "get",
            "do",
            "break",
            "pay",
            "catch",
            "reach",
            "come",
            "go",
            "keep",
            "save"
        ]
        return lvc
    def enframing_constructs(self):
        ec = [
            "believe",
            "think",
            "said",
            "suppose",
            "suspect",
            "guess",
            "understand",
            "wonder",
            "insist",
            "declare",
            "prefer",
            "order",
            "require"
        ]
        # typically paired with *that* and clause
        return ec
    def common_collocs(self):
        np = [
            "make sure",
            "be sure",
            'have a bath',
            'have a drink',
            'have a good time',
            'have a haircut',
            'have a holiday',
            'have a problem',
            'have a relationship',
            'have a rest',
            'have lunch',
            'have sympathy',
            'do business',
            'do nothing',
            'do someone a favour',
            'do the cooking',
            'do the housework',
            'do the shopping',
            'do the washing up',
            'do your best',
            'do your hair',
            'do your homework',
            'make a difference',
            'make a mess',
            'make a mistake',
            'make a noise',
            'make an effort',
            'make furniture',
            'make money',
            'make progress',
            'make room',
            "make trouble",
            "take a break",
            "take a chance",
            "take a look",
            "take a rest",
            "take a seat",
            "take a taxi",
            "take an exam",
            "take notes",
            "take someone's place",
            "take someone's temperature",
            'break a habit',
            'break a leg',
            'break a promise',
            'break a record',
            'break a window',
            "break someone's heart",
            'break the ice',
            'break the law',
            'break the news to someone',
            'break the rules',
            'catch a ball',
            'catch a bus',
            'catch a chill',
            'catch a cold',
            'catch a thief',
            'catch fire',
            'catch sight of',
            "catch someone's attention",
            "catch someone's eye",
            'catch the flu',
            "reach an agreement",
            'pay a fine',
            'pay attention',
            'pay by credit card',
            'pay cash',
            'pay interest',
            'pay someone a compliment',
            'pay someone a visit',
            'pay the bill',
            'pay the price',
            'pay your respects',
            'save electricity',
            'save energy',
            'save money',
            "save one's strength",
            'save someone a seat',
            "save someone's life",
            'save something to a disk',
            'save space',
            'save time',
            'save yourself the trouble',
            'keep a diary',
            'keep a promise',
            'keep a secret',
            'keep an appointment',
            'keep calm',
            'keep control',
            'keep in touch',
            'keep quiet',
            "keep someone's place",
            'keep the change',
            'come close',
            'come complete with',
            'come direct',
            'come early',
            'come first',
            'come into view',
            'come last',
            'come late',
            'come on time',
            'come prepared',
            'come right back',
            'come second',
            'come to a compromise',
            'come to a decision',
            'come to an agreement',
            'come to an end',
            'come to a standstill',
            'come to terms with',
            'come to a total of',
            'come under attack',
            'go abroad',
            'go astray',
            'go bad',
            'go bald',
            'go bankrupt',
            'go blind',
            'go crazy',
            'go dark',
            'go deaf',
            'go fishing',
            'go mad',
            'go missing',
            'go on foot',
            'go online',
            'go out of business',
            'go overseas',
            'go quiet',
            'go sailing',
            'go to war',
            'go yellow',
            'get a job',
            'get a shock',
            'get angry',
            'get divorced',
            'get drunk',
            'get frightened',
            'get home',
            'get lost',
            'get married',
            'get nowhere',
            'get permission',
            'get pregnant',
            'get ready',
            'get started',
            'get the impression',
            'get the message',
            'get the sack',
            'get upset',
            'get wet',
            'get worried'
        ]
        return np
