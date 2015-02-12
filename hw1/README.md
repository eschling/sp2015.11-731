There are five Python programs here (`-h` for usage):

 - `./align` aligns words using Dice's coefficient.
 - `./check` checks for out-of-bounds alignment points.
 - `./grade` computes alignment error rate.
 - `./ibm1` aligns sentences using ibm1
 - `symmetrize.py` symmetrizes alignments

The commands are designed to work in a pipeline. For instance, this is a valid invocation:

    ./align -t 0.9 -n 1000 | ./check | ./grade -n 5

##Final Model:

###Preprocessing:

The data is lowercased. The German side of the corpus is compound split using the cdec compound-split tool, and a map of the indices in the compound split German back to the original German is printed out during compound splitting.

###IBM Model 1:

./ibm1 -b bitext -n numsents -i niters [-o param\_outfile -c compound\_index\_map --backwards]

IBM Model 1 trained with EM. Parameters are initialized only for those words which appear in aligned sentences. The NULL word is added to the beginning of every source sentence. If a compound index map is provided, the source side of the bitext is assumed to be compound split, and after alignment the source alignments are mapped back to original indices. If --backwards is used, the target is assumed to be compound split.

The final output was run for 10 EM iterations.

###Symmetrization:

python symmetrize.py -f forwards.al -b backwards.al [--gdfa]

After running ibm1 forwards and backwards, the alignments are symmetrized using symmetrize.py with grow-diag. If --gdfa is used, it symmetrizes with grow-diag-final-and.

###Data:

The `data/` directory contains a fragment of the German/English Europarl corpus.

 - `data/dev-test-train.de-en` is the German/English parallel data to be aligned. The first 150 sentences are for development; the next 150 is a blind set you will be evaluated on; and the remainder of the file is unannotated parallel data.

 - `data/dev.align` contains 150 manual alignments corresponding to the first 150 sentences of the parallel corpus. When you run `./check` these are used to compute the alignment error rate. You may use these in any way you choose. The notation `i-j` means the word at position *i* (0-indexed) in the German sentence is aligned to the word at position *j* in the English sentence; the notation `i?j` means they are "probably" aligned.

