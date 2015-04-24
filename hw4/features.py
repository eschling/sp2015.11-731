#coding:utf8
import sys
import argparse
import gzip
import utils
import cPickle
from collections import defaultdict
from sklearn.feature_extraction import DictVectorizer

def get_feature_list(featext, infile, parse_file, gold=None, parse_features=False):
  parses = utils.read_dep_trees(parse_file)
  with open(infile) as f:
    for n, line in enumerate(f):
      if not line.strip(): continue
      parse = parses.next()
      if n%1000 == 0:
        sys.stderr.write('.')
      target, left, right = get_target(line)
      if gold:
        feats = featext.get_features(target, left, right, gold[n], parse, parse_features=parse_features)
      for j, k in enumerate(featext.ttable[target].keys()):
        if not gold:
          feats = featext.get_features(target, left, right, k, parse, parse_features=parse_features)
        yield feats

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--input', default='data/train.input', help='input sentences to extract features from')
parser.add_argument('-d', '--dev', default='data/dev+test.input')
parser.add_argument('-p', '--parses', default='data/train.parses.gz')
parser.add_argument('--dev_parses', default='data/dev+test.parses.gz')
parser.add_argument('-o', '--out', default='data/train.features.gz', help='Output file for extracted features')
parser.add_argument('--parse_features', default=False, action='store_true')
parser.add_argument('-t', '--ttable', default='data/ttable.filt')
parser.add_argument('--ttable_features', default=False, action='store_true')
parser.add_argument('-w', '--window', type=int, default=3)
parser.add_argument('--baseline', default=False, action='store_true')
parser.add_argument('--train_refs', default='data/train.refs')
parser.add_argument('--dev_refs', default='data/dev.refs')

args = parser.parse_args()

if args.baseline: args.window = 0

def get_target(line):
  split_line = line.strip().decode('utf8').split('|||')
  if len(split_line) == 2:
    left = []
    target = split_line[0].strip()
    right = split_line[1].strip().split()
  else:
    left = split_line[0].strip().split()
    target = split_line[1].strip()
    right = split_line[2].strip().split()
  return target, left, right

train_gold = []
with open(args.train_refs) as f:
  for line in f:
    if not line.strip(): continue
    train_gold.append(line.strip().decode('utf8'))
print 'train gold: ', len(train_gold)
dev_gold = []
with open(args.dev_refs) as f:
  for line in f:
    if not line.strip(): continue
    dev_gold.append(line.strip().decode('utf8'))
print 'dev gold:', len(dev_gold)

ft = DictVectorizer(sparse=True)
featext = utils.FeatureExtractor(args.ttable)

with gzip.open(args.out, 'wb') as out:
  cPickle.dump(train_gold, out, -1)
  cPickle.dump(dev_gold, out, -1)
  parses = utils.read_dep_trees(args.dev_parses)
  dev_feats, dev_labels = [], []
  test_feats, test_labels = [], []
  with open(args.dev) as f:
    for n, line in enumerate(f):
      if not line.strip(): continue
      parse = parses.next()
      target, left, right = get_target(line)
      if n%1000==0:
        sys.stderr.write('.')
      flist = []
      flabels = []
      for cz in featext.ttable[target].keys():
        flist.append(featext.get_features(target, left, right, cz, parse, parse_features=args.parse_features))
        flabels.append(cz)
      if n < len(dev_gold):
        dev_feats+=flist
        dev_labels.append(flabels)
      else:
        test_feats+=flist
        test_labels.append(flabels)
  ft.fit(dev_feats+test_feats)
  dev_feats = ft.transform(dev_feats)
  test_feats = ft.transform(test_feats)
  print 'dev feats:', dev_feats.shape
  print 'test feats:', test_feats.shape
  cPickle.dump(dev_feats, out, -1)
  cPickle.dump(test_feats, out, -1)
  cPickle.dump(dev_labels, out, -1)
  cPickle.dump(test_labels, out, -1)
  test_labels = []
  dev_labels = []
  dev_feats = []
  test_feats = []
  sys.stderr.write('\ndev\n')

  train_feats = ft.transform(get_feature_list(featext, args.input, args.parses, gold=train_gold, parse_features=args.parse_features))
  print 'positive:', train_feats.shape
  cPickle.dump(train_feats, out, -1)
  sys.stderr.write('\npositive\n')
 
  train_feats = None
  train_feats = ft.transform(get_feature_list(featext, args.input, args.parses, parse_features=args.parse_features))
  print 'negative:', train_feats.shape
  cPickle.dump(train_feats, out, -1)

  weights = ft.transform([{'log_prob_tgs':1.0}])
  cPickle.dump(weights, out, -1) 
