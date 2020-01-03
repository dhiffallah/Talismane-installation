import subprocess as sp
import os
CWD = os.path.abspath(os.curdir)
JAVA_PATH = "/usr/bin/java"
TALISMANE = CWD + "/talismane/talismane-distribution-5.1.0-bin"
TEXT_FILE = CWD + "/data/text.txt"
OUTPUT_FILE = CWD + "/data/talismane_output.txt"
DUMP = "dump"


def parse_raw_text_file(path_to_file, path_to_output=OUTPUT_FILE):
    """
    from a raw text file writed in french, process the talismane syntax analyzer to produce a matching conll file
    :@param path_to_file:
    :@return: a conll file
    """
    f = open(DUMP, 'w')
    command = [
        JAVA_PATH,
        "-Xmx1G",
        "-Dconfig.file=" + TALISMANE + "/talismane-fr-5.0.4.conf",
        "-jar",
        TALISMANE + "/talismane-core-5.1.0.jar",
        "--analyse",
        "--sessionId=fr",
        "--encoding=UTF8",
        "--inFile=" + path_to_file,
        "--outFile=" + path_to_output,
    ]

    sub_execute = sp.run(command, stdout=f)
    f.close()
    return sub_execute
    # print(parse_raw_text_file("outPutCleaner.txt"))

if __name__ == '__main__':
    print(parse_raw_text_file("data/text.txt"))
