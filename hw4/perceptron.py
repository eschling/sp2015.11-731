import argparse
import json
import random
import sys
import gzip
import cPickle
from scipy.sparse import csr_matrix
import numpy as np

DIR='/usr3/home/eschling/mt/hw4'

parser = argparse.ArgumentParser()

parser.add_argument('-a', '--alpha', type=float, default=0.1)
parser.add_argument('-l', '--l2', type=float)
parser.add_argument('--hinge', type=float, default=0.0)
parser.add_argument('--iters', type=int, default=100)
parser.add_argument('-b', '--best_output')
parser.add_argument('-p', '--pickle')

args = parser.parse_args()

pickle_file = gzip.open(args.pickle, 'rb')
train_gold = cPickle.load(pickle_file)
dev_gold = cPickle.load(pickle_file)
sys.stderr.write('train_gold: {}, dev_gold: {}\n'.format(len(train_gold), len(dev_gold)))

dev_feats = cPickle.load(pickle_file)
test_feats = cPickle.load(pickle_file)
sys.stderr.write('dev_feats: {}, test_feats: {}\n'.format(dev_feats.shape, test_feats.shape))

dev_labels = cPickle.load(pickle_file)
test_labels = cPickle.load(pickle_file)
sys.stderr.write('test_labels: {}, dev_labels: {}\n'.format(len(test_labels), len(dev_labels)))

train_feat_pos = cPickle.load(pickle_file)
train_feat_neg = cPickle.load(pickle_file)
sys.stderr.write('neg: {}, pos: {}\n'.format(train_feat_neg.shape, train_feat_pos.shape))

weights = cPickle.load(pickle_file).todense()
sys.stderr.write('weights: {}\n'.format(weights.shape))
pickle_file.close()

adagrad = csr_matrix(weights.shape).todense()
average = csr_matrix(weights.shape).todense()
sys.stderr.write('data loaded\n')

def write_best(weights):
  with open(args.best_output, 'w') as out:
    score_vector = dev_feats * weights.T
    i = 0
    for n, gold in enumerate(dev_gold):
      scores = []
      for j, cz in enumerate(dev_labels[n]):
        tpl = (score_vector[i+j][0], cz)
        scores.append(tpl)
      i += len(dev_labels[n])
      scores.sort(key=lambda x: x[0], reverse=True)
      candidates = [x[1] for x in scores]
      out.write(' ||| '.join(candidates).encode('utf-8')+'\n')
    score_vector = test_feats * weights.T
    i = 0
    for n in range(len(test_labels)):
      scores = []
      for j, cz in enumerate(test_labels[n]):
        tpl = (score_vector[i+j][0], cz)
        scores.append(tpl)
      i += len(test_labels[n])
      scores.sort(key=lambda x: x[0], reverse=True)
      candidates = [x[1] for x in scores]
      out.write(' ||| '.join(candidates).encode('utf-8')+'\n')

def score_dev(current_weights):
  dev_mrr = 0.0
  score_vector = dev_feats * current_weights.T
  i = 0
  for n, gold in enumerate(dev_gold):
    scores = []
    for j, cz in enumerate(dev_labels[n]):
      tpl = (score_vector[i+j][0], cz)
      scores.append(tpl)
    i += len(dev_labels[n])
    for j, (sc, cz) in enumerate(sorted(scores, key=lambda x: x[0], reverse=True)):
      if cz==gold:
        dev_mrr += 1.0/(j+1.0)
        break
  dev_mrr = dev_mrr/len(dev_gold)
  sys.stderr.write('dev : {}\n'.format(dev_mrr))
  return dev_mrr

prev_dev = None
score_dev(weights)
for i in range(args.iters):
  scores = args.hinge - (train_feat_pos - train_feat_neg).dot(weights.T)
  scores[scores < 0] = 0.0
  loss = np.sum(scores)/train_feat_pos.shape[0]
  grad = (scores.T*(train_feat_neg - train_feat_pos))
  if args.l2: grad += 2*args.l2*weights # fake l2
  grad /= train_feat_neg.shape[0]
  adagrad += np.power(grad, 2)
  weights -= np.multiply(grad, np.where(adagrad != 0.0, args.alpha/np.sqrt(adagrad), 0.0))
  if i%1==0:
    sys.stderr.write('{}: {:.2f} '.format(i+1, loss))
    mrr = score_dev(weights)
    if mrr > prev_dev:
      prev_dev = mrr
      if args.best_output: write_best(weights)
  elif i: sys.stderr.write('.')
