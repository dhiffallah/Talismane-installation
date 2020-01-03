from copy import copy
from sys import argv
import re

# creating 4 major classes for document analysis : Document, Sentence,
# Tokens and Chunks to facilite semantic parsing

NUMBERS = [
    "un",
    "deux",
    "trois",
    "quatre",
    "cinq",
    "six",
    "sept",
    "huit",
    "neuf",
    "dix",
    "onze",
    "douze",
    "treize",
    "quatorze",
    "quinze",
    "seize",
    "vingt",
    "trente",
    "quarante",
    "cinquante",
    "soixante",
    "cent",
    "cents",
    "mil",
    "mille",
    "million",
    "millions",
    "milliard",
    "milliards"
]


def doc_from_file(path_to_file, verbose=False):
    """
    main access point to generate Doc/Sent/Chunk/Token by giving a .conll file an input.
    @input : CONLL file
    @output : a Python "representation"  or "structure" for the 4  classes (DOC, SENT, CHUNK, TOKENS)
    """

    doc = Doc()
    current_sentence = Sentence(doc=doc)
    with open(path_to_file, 'r') as f:
        for line in f.readlines():
            if verbose:
                print(line[:-1])
            if line == '\n':

                if current_sentence.tokens != list():
                    current_sentence.update_token_head()
                    doc.add_sent(copy(current_sentence))
                doc.raw += current_sentence.read()
                current_sentence = Sentence(doc=doc)
            else:
                raw_token = line[:-1].split('\t')
                token = Token(
                    raw_token[0],
                    raw_token[1],
                    raw_token[2],
                    raw_token[3],
                    raw_token[5],
                    raw_token[6],
                    raw_token[7]
                )
                current_sentence.add_token(token)
    for sent in doc.sents:
        sent.update_token_head()

    if verbose:
        # print(doc)
    return doc


class Doc:
    """
    the Doc class contains parsed sentences of the input file
    """

    def __init__(self):
        self.raw = str()
        self.sents = list()
        self.numbers = None
        self.distances = None

    def __str__(self):
        return "\n".join([str(e) for e in self.sents])

    def add_sent(self, sentence):
        self.sents.append(sentence)
        sentence.doc = self

    def get_number(self, token):
        """
        easy access to numeric entity by associated token
        """
        return self.numbers[self.get_token_full_id(token)]

    def get_type(self, token):
        """
        easy access to num entity types
        """
        measure, unit, qty, ref = self.get_number(token)
        return (measure, unit, ref)

    def is_question(self):
        """
        "a naïve value"
        Check if Doc is a question
        """
        is_quest = False
        regexp = re.compile(r"""^[A-Z].*\?$""")
        if re.match(regexp, self.raw):
            is_quest = True
        return is_quest

    def view_number(self, toktokensen):
        """
        string of the number associated to the token
        """
        tok_id = self.get_token_full_id(token)
        unit = ' ' + str(self.numbers[tok_id][1])
        ref = ' ' + str(self.numbers[tok_id][3])
        if unit == ' _':
            unit = ''
        if ref == ' _':
            ref = ''
        return str(self.numbers[tok_id][2]) + unit + ref

    def get_token_full_id(self, token):
        return token.sent.id * 1000 + token.id

    def token_from_full_id(self, _id):
        tok_id = _id % 1000
        sent_id = (_id - tok_id) // 1000
        for sent in self.sents:
            if sent_id == sent.id:
                for token in sent.tokens:
                    if tok_id == token.id:
                        return token


class Sentence:
    """
    a sentence is inside a Doc and contains Differents chunks and tokens
    """

    def __init__(self, doc=None):
        """
        :@param doc: is the parent Doc instance
        """
        self.doc = doc
        if doc is None:
            self.id = None
        else:
            self.id = len(doc.sents)
        self.tokens = list()
        self.chunks = list()  # by default, no chunk. they need to be computed
        self.raw_text = None

    def __str__(self):
        s = ""
        s = s + "ID" + "\t" + "WORD" + "\t" + "LEMMA" + "\t" + \
            "POS" + "\t" + "HEAD" + "\t" + "DEP" + "\t" + "FEATS"
        s = s + "\n" + "\n".join([str(t) for t in self.tokens])
        return s

    def read(self):
        return " ".join([e.word for e in self.tokens])

    def __eq__(self, sentence):
        return isinstance(
            sentence, Sentence) and self.doc == sentence.doc and self.id == sentence.id

    def select_by_pos(self, pos):
        """
        check if pos equal to pos
        """
        res = list()
        for token in self.tokens:
            if token.pos == pos:
                res.append(token)

        return res

    def add_token(self, token):
        """
        add the instance of Token to the sentence
        @:param token: a Token instance
        """
        self.tokens.append(token)
        token.sent = self

    def update_token_head(self):
        """
        transform every int Token.head to a Token reference
        """
        for token in self.tokens:
            if isinstance(token.head, int):
                if token.head is 0:
                    token.head = None
                else:
                    token.head = self.tokens[token.head - 1]
        self.dep_tree_build()

    def dep_tree_build(self):
        """
        build a tree based on dependency relations
        the tree values are id of head dep
        """
        self.tree = dict()
        for token in self.tokens:
            if token.head is not None:
                self.tree[token.id] = token.head.id

    def get_chunk(self, ch_type):
        """
        return all chunks belonging to the matching type
        :@param ch_type: should be 'SUJ', 'CONT', 'OBJ', 'CONJ', 'UNK', 'VRB'
        """
        res = list()
        for chunk in self.chunks:
            if chunk.type == ch_type:
                res.append(copy(chunk))
        return res

    def chunk(self):
        """
        chunker for sentence, splitting it into different roles :
        SUB for subject group / example:  "Il" mange
        CONT for context (place, time, ...) / example : Il mange "le soir"
        OBJ for objects / example : Il mange "une pomme"
        CONJ for conjonction / example : IL mange "une pomme et une orange"
        VRB for verb group /example : Il "mange"
        UNK for unknown group /  for all the rest of group except the precedent groups
        """
        if self.tree is None:
            raise ValueError(
                "self.tree not instancied yet. Should run dep_tree_build before.")

        # get tokens connected to root
        dep_type = {
            'mod': 'CONT',
            'suj': 'SUJ',
            'obj': 'OBJ',
            'coord': 'COORD',
            'ponct': 'UNK',
            'aff': 'VRB',
            'ats': 'VRB',
            'ato': 'VRB',
            'p_obj': 'OBJ',
            'a_obj': 'OBJ',
            'mod_rel': 'CONT',
            'prep': 'OBJ',
                    'root': 'OBJ',
                    'dep': 'OBJ',
                    'det': 'SUJ'
        }

        to_root = list()
        unexplored_tokens = copy(self.tokens)

        for token in self.tokens:
            if token.head is None:
                unexplored_tokens.remove(token)
                # the main verb of the sentence should be connected to root
                # if the pos is a verb, then the chunk_type is "VRB"
                if token.pos in ["V", "VPP", "VS", "VPR", "VIMP"]:
                    verb_chunk = Chunk(self)
                    verb_chunk.type = "VRB"
                    verb_chunk.tokens.append(copy(token))
                    # now, will find all tokens belonging to verb group
                    to_do = token.get_dependants()
                    while to_do != list():
                        current = self.tokens[to_do.pop() - 1]
                        if current.dep in ["aux_tps", "aux_pass", "aux_caus"]:
                            to_do += current.get_dependants()
                            verb_chunk.tokens.append(copy(current))
                            unexplored_tokens.remove(current)
                    # sort the chunk verbs according to the order of token
                    # "verb" in this case
                    verb_chunk.sort()
                    self.chunks.append(verb_chunk)
                # there can be other parts linked to root without
                else:
                    other_chunk = Chunk(self)
                    for index in token.get_group()[0]:
                        other_chunk.tokens.append(self.tokens[index - 1])
                    other_chunk.sort()
                    self.chunks.append(other_chunk)
        # make a list of all tokens in VRB chunk
        vrb_ch_tok = list()
        for chunk in self.get_chunk('VRB'):
            vrb_ch_tok += copy(chunk.tokens)
        vrb_ch_tok = [item.id for item in vrb_ch_tok]
        for token in unexplored_tokens:
            if token.head.id in vrb_ch_tok:
                new_chunk = Chunk(self)
                new_chunk.type = dep_type[token.dep]
                for index in token.get_group()[0]:
                    new_chunk.tokens.append(self.tokens[index - 1])
                new_chunk.sort()
                self.chunks.append(copy(new_chunk))
        self.chunk_sort()
        for chunk in self.chunks:
            chunk.update()
        return chunk

    def chunk_sort(self):
        """
        sort chunks by 1st token order
        """
        self.chunks.sort(key=lambda x: x.tokens[0].id)

    def show_struct(self):
        """
        show the structure of the phrase (by chunks)
        """
        for chunk in self.chunks:
            print(chunk.type, end=" ")


class Chunk:
    """
    a chunk is inside a sentence and contains tokens
    """

    def __init__(self, sent):
        """
        :@param sent: is the parent sentence of the chunk
        """
        self.sent = sent
        # the type of the chunk can be 'SUJ', 'CONT', 'OBJ', 'CONJ', 'UNK',
        # 'VRB'
        self.type = str('UNK')
        self.feats = dict()
        self.tokens = list()

    def __str__(self):
        return " ".join([str(e.word) for e in self.tokens]) + " /" + self.type

    def update(self):
        for token in self.tokens:
            token.feats['type'] = self.type

    def sort(self):
        """
        reorganize the tokens in the list by the order in the sentence
        """
        self.tokens.sort(key=lambda x: x.id)


class Token:
    """
    a token is inside a chunk and contains all properties
    """

    def __init__(self, wid, word, lemma, pos, feats, head, dep):
        """
        :@param id: the token id
        :@param word: the original word
        :@param lemma: the lemma of each word
        :@param pos: the pos of  each word
        :@param feats: a string like 'att1=val1,val2|att2=val3|att3=val4' "trait morphologique (masculin,singulier,pluriel,féminin")
        :@param head: an int matching another token id (or root for 0)
        :@param dep:The dependancy label
        """
        self.sent = None
        self.id = int(wid)
        self.word = str(word)
        self.lemma = str(lemma)
        self.pos = str(pos)
        # building feats need a bit more treatment
        self.feats = dict()
        raw_feats_list = feats.split('|')

        for item in raw_feats_list:
            if item != str():
                att, value = item.split('=')
                values = tuple(value.split(','))
                self.feats[att] = values
        # should be a token or None if root or int if the token is not yet
        # created
        self.head = int(head)
        self.dep = str(dep)

    def __str__(self):
        row = list()
        row += [str(self.id), self.word, self.lemma, self.pos]

        if self.head is None:
            row.append("root")
        else:
            row.append(str(self.head.id))

        row.append(self.dep)

        for key, value in self.feats.items():
            row.append(str(key) + "=" + str(value))
        return "\t".join(row)

    def __eq__(self, token):
        return isinstance(
            token, Token) and self.sent == token.sent and self.id == token.id and self.word == token.word

    def next(self):
        """
        return the following token in the sentence
        """
        sent_index = self.sent.tokens.index(self)
        if sent_index == len(self.sent.tokens) - 1:
            return None
        else:
            return self.sent.tokens[sent_index + 1]

    def previous(self):
        """
        return the preceding token in the sentence
        """
        sent_index = self.sent.tokens.index(self)
        if sent_index == 0:
            return None
        else:
            return self.sent.tokens[sent_index - 1]

    def get_group(self):
        """
        from the current token, get all indices of token attached to it
        (with itself included)
        """

        grp_type = self.dep
        group = [self.id]
        #print("getting group from {}".format(str(self.word)))
        if self.id not in self.sent.tree.values():
            #print("(1) returning ({},{})".format(group,grp_type))
            return group, grp_type
        else:
            for key, value in self.sent.tree.items():
                if self.id == value:
                    to_add = self.sent.tokens[key - 1].get_group()[0]
                    group += to_add
            #print("(2) returning ({},{})".format(group,grp_type))
            return group, grp_type

    def get_dependants(self):
        """
        return all the tokens linked to self
        """

        dependants = list()
        for key, value in self.sent.tree.items():
            if self.id == value:
                dependants.append(key)

        return dependants

    def is_number(self):
        """
        check if token contains a number
        """
        if self.word in NUMBERS and self.word.lower() != 'un':
            return True

        regexp = re.compile(r"""[0-9]+[,.]?[0-9]*([eE][0-9]+)?""")
        if re.match(regexp, self.word):
            return True

        return False

    def is_currency(self):
        """
        check if token is currency  "euros , francs, $ ,€ "
        """
        is_curr = False
        regexp = re.compile(r"""(euros|Francs|\$|€|EUROS|francs)+""")
        matchgroup = re.match(regexp, self.word)
        if re.match(regexp, self.word):
            is_curr = True
        return is_curr

    def distance(self, token):
        """
        a naïve distance by position in phrase
        :return dist: is -1 if tokens are not in the same sentence, else return
        the number of tokens between self and token
        """

        if self == token:
            return 0

        left, right = self.previous(), self.next()
        dist = 1
        while left != token and right != token:
            dist += 1
            none_count = 0

            if left is not None:
                left = left.previous()
            else:
                none_count += 1
            if right is not None:
                right = right.next()
            else:
                none_count += 1

            if none_count == 2:
                return -1

        return dist


if __name__ == '__main__':
    doc = doc_from_file(argv[1])
    print("**** Doc generating from connl file ****")
    print(doc)
