import talismane_built_structure as tbs
import talismane_analysis as tal
from collections import Counter
import sys


def extract_keywords(document):
    """
    Extract keywords from contrcat using
    "Talismane"
    """
    key_words = []
    for sent in document.sents:
        for token in sent.tokens:
            #print("ID:" ,token.id ,"  Word: ",token.word ," Pos: ", token.pos ," Dep: ", token.dep ,"Dependants: ", token.get_dependants() , " Distance: ", token.distance(token.word) , " Get group : ",token.get_group() )
            if (token.pos == "NC" and (token.dep == 'prep' or token.dep == "obj" or token.dep == "dep_coord") and
                    (token.head.pos == "P" or token.head.pos == "VINF" or token.head.pos == "P+D"or token.head.pos == "CC") or
                    ((token.word == "VPP" or token.word == "V" or token.word == "VINF") and (token.dep == "obj" or token.dep == "sub" or token.dep == "root") and
                     (token.head.pos == "V" or token.head.pos == "CS" or token.head.pos == "root" or token.head.pos == "VPR") or
                     (token.pos == "ADJ" and token.dep == 'mod' and token.head.pos == "NC")) and (token.is_number() == False) and (token.is_currency() == False)):
                key_words.append(token.word)
    key_words = Counter(key_words)
    return key_words


def extract_chunk(document):
    """
    Extract Groups Chunks :
    A chunk  can be : SUJ, OBJ, VRB, CONT, UNK
    """
    list_groups = list()
    raw_text = document.raw
    for sent in document.sents:
        print("*****************LOAD CHUNK*********************")
        print("Talismane chunk : ", sent.chunk())


if __name__ == '__main__':
    if len(sys.argv) is 2:
        tal.parse_raw_text_file(
            sys.argv[1],
            path_to_output="data/talismane_output.txt")
        print("*****************FILE PARSED*****************")
    docs = tbs.doc_from_file("data/talismane_output.txt")
    print(extract_keywords(docs))
    print(extract_chunk(docs))
