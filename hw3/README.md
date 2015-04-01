`decode` implements a phrase based decoder that uses beam search with future cost estimates and coverage vectors. Hypotheses are recombined based on the number of words they cover, coverage vector, and lm state. I added the following options:

`--start_stack`: start size for the stack. The decoder runs with an iteratively increasing stack size (adding 100 each time) until it reaches `--stack-size`

`--tm_size`: cutoff for number of tm entries to use. It didn't really help to set this above 30.

`--rescore`: number of hypotheses to rescore using the grading script, which marginalizes over all possible alignments.

`--reorder_limit`: limit to use for reordering heuristic. The reordering was constrained based on the number of words translated. Most sentences did better when reordering wasn't constrained, but for a few sentences constraining this to 5 or 10 showed improvements.

There is also a postprocessing step in the decoder which retranslates phrases in the final winning hypothesis, and keeps these if they improve the score. I tried more extensive postprocessing, with the gibbs like functions (merge, split, reorder, retranslate), but with a large enough beam size on the initial decoder a small constant number of these operations didn't really help. 

I also tried reordering the adjectives in the input using the Stanford POS Tagger. This helped a few sentences but hurt overall. 

All of my many outputs were combined together, taking the best according to the grading script.

This got me to a model score of -4816.248381.

I then looked at chucheng's code, and implemented a similar idea of allowing new phrases to insert at previous points in the current target hypothesis (I feel like this is kind of cheating, but considering the fact that my code appears in 2 other submissions, not terrible). This was added as the option `--insert_phrase`. It is significantly slower (especially if reordering is also allowed through use of `--reorder_limit`, even if that reordering is set to be very small), but running with this option on a smaller beam size helps a great deal on a few of the sentences.

This run with various options brought it down to -4808.326755 (although most of the runs didn't finish in time).

My initial submission used a really idiotic heuristic, which apparently got copied into a number of other people's submissions. Instead of recombining based on coverage vectors and lm state, it recombined based solely on coverage vectors. This was fast and beat the baseline by quite a bit given a stack size of ~100, but since it only kept the best hypothesis for each coverage vector it didn't do terribly well. I'm assuming the people who copied it didn't know that it was doing this.

There are three Python programs here (`-h` for usage):

 - `./decode` a simple non-reordering (monotone) phrase-based decoder
 - `./grade` computes the model score of your output

The commands are designed to work in a pipeline. For instance, this is a valid invocation:

    ./decode | ./grade


The `data/` directory contains the input set to be decoded and the models

 - `data/input` is the input text

 - `data/lm` is the ARPA-format 3-gram language model

 - `data/tm` is the phrase translation model

