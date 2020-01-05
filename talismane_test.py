import talismane_built_structure as tbs
import talismane_analysis as tal
import sys


def display_token_features(document):
    """
    display  talisamane token features 
    
    """
    for sent in document.sents:
        for token in sent.tokens:
            print("ID: " ,token.id ,"  Word: ",token.word ," Pos: ", token.pos ," Dep: ", token.dep ,"Dependants: ", token.get_dependants() , " Distance : ", token.distance(token.word) , " Get group : ",token.get_group() )
            


def extract_chunk(document):
    """
    Extract Groups Chunks :
    A chunk  can be : SUJ, OBJ, VRB, CONT, UNK
    """
    for sent in document.sents:
        print("Talismane chunks : ", sent.chunk())


if __name__ == '__main__':
    if len(sys.argv) is 2:
        tal.parse_raw_text_file(
            sys.argv[1],
            path_to_output="data/talismane_output.txt")
        print("*****************FILE PARSED*****************")
    docs = tbs.doc_from_file("data/talismane_output.txt")
    print(display_token_features(docs))
    print(extract_chunk(docs))
