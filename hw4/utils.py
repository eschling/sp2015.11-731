#coding:utf8
import re
import sys
import gzip
from collections import defaultdict
from collections import Counter
def read_ttable(filename):
        czech_counts = Counter()
	translation_table = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
	print >>sys.stderr, 'Reading ttable from %s...' % filename
	with open(filename) as f:
		for i, line in enumerate(f):
			source, target, features = [part.strip() for part in line.decode('utf-8').strip().split('|||')]
			#if not re.search(r'[a-záčďéěíňóřšťúůýž]', target): continue
                        czech_counts.update(target.split())
			features = [float(v) for v in features.split()]
			assert len(features) == 4
			features = { 'log_prob_tgs': features[0], \
				     'log_prob_sgt': features[1], \
				     'log_lex_prob_tgs': features[2], \
				     'log_lex_prob_sgt': features[3] }
			translation_table[source][target] = features
			sys.stderr.write('%d\r' % i)
	print >>sys.stderr
	return translation_table, czech_counts

class FeatureExtractor:
	def __init__(self, ttable):
		tt, counts = read_ttable(ttable)
                self.ttable = tt
		self.counts = counts
		self.ttcounts = dict()

	def get_features(self, phrase, left, right, cz, parse, parse_features=False):
		feats = defaultdict(float)
		sent_len = len(left) + len(right) + len(phrase.split())
		indices = [len(left)+i for i in range(len(phrase.split()))]
		if phrase not in self.ttcounts:
			ttable_counts = defaultdict(int)
			for key in self.ttable.keys():
				if not phrase in key: continue
				for target in self.ttable[key].keys():
					for cz in self.ttable[phrase].keys():
						if cz in target: ttable_counts[cz] += 1.0
			self.ttcounts[phrase] = ttable_counts
		for k, w in enumerate(cz.split()):
      			feats['target_count_'+str(k)] = float(self.counts[w])
		if cz in self.ttcounts[phrase]:
			feats['ttable_count'] = self.ttcounts[phrase][cz]
		for name, prob in self.ttable[phrase][cz].items():
			feats[name] = prob
  		#prevw = (left[-1] if len(left) > 0 else '')
  		#nextw = (right[0] if len(right) > 0 else '')
  		#feats['src_'+phrase+'_tgt_'+cz+'_prev_'+prevw] = 1.0
  		#feats['src_'+phrase+'_tgt_'+cz+'_next_'+nextw] = 1.0
  		feats['suff_'+cz[-2:]] = 1.0
  		feats['target_'+phrase+'_suff_'+cz[-2:]] = 1.0
  		feats['lex_'+phrase+'_target_'+cz] = 1.0
  		pos = ' '.join(parse.tags[i] for i in indices)
  		feats['pos_'+pos+'_suff_'+cz[-2:]] = 1.0
		prevp = (parse.tags[indices[0]-1] if indices[0]-1 > 0 else '<s>')
                nextp = (parse.tags[indices[-1]+1] if indices[-1]+1 < len(parse.tags) else '</s>')
                feats['src_'+phrase+'_tgt_'+cz+'_prevp_'+prevp] = 1.0
                feats['src_'+phrase+'_tgt_'+cz+'_nextp_'+nextp] = 1.0
		feats['pos_'+pos+'_tgt_'+cz+'_prevp_'+prevp] = 1.0
                feats['pos_'+pos+'_tgt_'+cz+'_nextp_'+nextp] = 1.0
		if parse_features:
			for ti in indices:
			 	feats['nchildren'] += len(parse.children[ti])
				if not parse.parents[ti][0]:
					feats['root_'+cz[-2:]] += 1
					feats['root_'+phrase+'_'+cz[-2:]] += 1
				else:
					p, rel = parse.parents[ti]
					feats['parentrel_'+rel+'_'+cz[-2:]] = 1.0
					feats['parentposrel_'+parse.tags[p]+'_rel_'+rel+'_'+cz[-2:]] = 1.0
					feats['parentpos_'+parse.tags[p]+'_'+cz[-2:]] = 1.0
				for i, rel in parse.children[ti]:
					feats['childrel_'+rel+'_'+cz[-2:]] += 1.0
                                        feats['childposrel_'+parse.tags[i]+'_rel_'+rel+'_'+cz[-2:]] += 1.0
                                        feats['childpos_'+parse.tags[i]+'_'+cz[-2:]] += 1.0
                return feats

class DependencyTree:
	def __init__(self, n):
		self.terminals = [None for _ in range(n)]
		self.tags = [None for _ in range(n)]
		self.children = [[] for _ in range(n)]
		self.parents = [None for _ in range(n)]
		self.roots = []

	@staticmethod
	def parse(input_string):
		input_lines = input_string.strip().split('\n')
		n = len(input_lines)
		tree = DependencyTree(n)
		for i, line in enumerate(input_lines):
			fields = [field.strip() for field in line.strip().split('\t')]
			j, terminal, _, tag, __, ___, parent, relation = fields
			j = int(j)
			parent = int(parent)
			assert i + 1 == j
			assert 1 <= j <= n
			assert 0 <= parent <= n
			tree.terminals[i] = terminal
			tree.tags[i] = tag
			if parent != 0:
				tree.parents[i] = (parent - 1, relation)
				tree.children[parent - 1].append((i, relation))
			else:
				tree.parents[i] = (None, relation)
				tree.roots.append((i, relation))

		return tree

def read_dep_trees(filename):
	current_tree = []
	with gzip.open(filename) as f:
		for line in f:
			line = line.decode('utf-8')
			if len(line.strip()) != 0:
				current_tree.append(line.strip())
			else:
				yield DependencyTree.parse('\n'.join(current_tree))
				current_tree = []
