#   Talismane Analyzer Installation  & Test
API for the Talismane tool for NLP projects :
- Installation and configuration of Talismane
- Launch of Talismane in  local mode

## Prerequisites and Installation
To analyse a text file in French, download the latest Talismane release at: https://github.com/urieli/talismane/releases

You need to download three files:

	talismane-distribution-X.X.X-bin.zip

	talismane-fr-X.X.X.conf

	frenchLanguagePack-X.X.X.zip

Unzip the file talismane-distribution-X.X.X-bin.zip, but not frenchLanguagePack-X.X.X.zip. Then copy the other two files into into the folder where talismane-distribution-X.X.X-bin.zip was unzipped.

Put the three scripts (talismane_analysis.py ,talismane_built_structure.py,Talismane_test.py ) in the same place as the french Language Pack
## Usage
- The file  "**talismane_analysis.py**" :  allows you to launch the TALISMANE synataxial analyzer.
- The file "**talismane_built_structure.py**" : main access point to generate Document/Sentence/Chunk/Token  by giving a .conll file an input.

## Tests
```python
Python3   <Talismane_test.py>  <path_to_file_text.txt>

```

## Authors
Dhifallah OTHMEN 
