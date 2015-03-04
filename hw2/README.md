There are four Python programs here (`-h` for usage):
 - `./meteor` computes the simple meteor metric (weited precision and recall), but with up to trigrams
 - `./evaluate` evaluates pairs of MT output hypotheses relative to a reference translation using counts of matched words
 - `./check` checks that the output file is correctly formatted
 - `./grade` computes the accuracy

###Solution

The submitted output is the result of running the `meteor` script on the provided data, preprocessed using the Snowball stemmer in nltk. For each reference, the script takes all unigram, bigrams, and trigrams and puts them into a set, computing the precision and recall against the same set for the reference. The precision and recall are combined into an fscore (the output uses f-3, with the parameter chosen by a grid search), and the translation with the highest fscore is chosen as the better one (or 0 if they're equal).

The commands are designed to work in a pipeline. For instance, this is a valid invocation:

    ./evaluate | ./check | ./grade

The `data/` directory contains the following two files:

 - `data/train-test.hyp1-hyp2-ref` is a file containing tuples of two translation hypotheses and a human (gold standard) translation. The first 26208 tuples are training data. The remaining 24131 tuples are test data.

 - `data/train.gold` contains gold standard human judgements indicating whether the first hypothesis (hyp1) or the second hypothesis (hyp2) is better or equally good/bad for training data.

Until the deadline the scores shown on the leaderboard will be accuracy on the training set. After the deadline, scores on the blind test set will be revealed and used for final grading of the assignment.
