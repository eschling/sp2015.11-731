#!/usr/bin/env python
import argparse
import sys
import models
import grade_util

parser = argparse.ArgumentParser(description='Compute unnormalized translation probability by marginalizing over alignments.')
parser.add_argument('-i', '--input', dest='input', default='data/input', help='File containing sentences to translate (default=data/input)')
parser.add_argument('-t', '--translation-model', dest='tm', default='data/tm', help='File containing translation model (default=data/tm)')
parser.add_argument('-l', '--language-model', dest='lm', default='data/lm', help='File containing ARPA-format language model (default=data/lm)')
parser.add_argument('--output_f', action='store_true', default=False)
parser.add_argument('-x', dest='x', default='test.1000')
parser.add_argument('-y', dest='y', default='1000.step')
opts = parser.parse_args()

tm = models.TM(opts.tm,sys.maxint)
lm = models.LM(opts.lm)

french_sents = [tuple(line.strip().split()) for line in open(opts.input).readlines()]
english_1 = [tuple(line.strip().split()) for line in open(opts.x).readlines()]
english_2 = [tuple(line.strip().split()) for line in open(opts.y).readlines()]

if (len(french_sents) != len(english_1) or len(english_1) != len(english_2)):
    sys.stderr.write("ERROR: French and English files are not the same length! Only complete output can be graded!\n")
    sys.exit(1)

logprob = 0.0

for i in range(len(french_sents)):
  english_1_grade = grade_util.grade(lm, tm, french_sents[i], english_1[i])
  english_2_grade = grade_util.grade(lm, tm, french_sents[i], english_2[i])
  win_e, win_score = max((english_1[i], english_1_grade), (english_2[i], english_2_grade), key=lambda (e, g): g)
  logprob += win_score
  if opts.output_f:
    if win_score == english_2_grade and english_2_grade > english_1_grade: print ' '.join(french_sents[i])
  else: print ' '.join(win_e)

sys.stderr.write('model score: {}\n'.format(logprob))
