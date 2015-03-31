#!/usr/bin/env python
import sys, os, nltk
from nltk.tag.stanford import POSTagger

os.environ['STANFORD_MODELS'] = '/usr3/home/eschling/tools/stanford-postagger-full-2014-08-27'
#os.environ['STANFORD_PARSER'] = '/usr3/home/eschling/tools/stanford-postagger-full-2014-08-27'
#os.environ['JAVAHOME'] = '/usr/local/java/jdk1.7.0_51'
tagger = POSTagger('models/spanish.tagger', '/usr3/home/eschling/tools/stanford-postagger-full-2014-08-27/stanford-postagger.jar', encoding='utf8')

with open('/home/eschling/projects/sp2015.11-731/hw3/data/input') as f:
    for line in f:
      text = line.strip().decode('utf8').split()
      text_pos = tagger.tag(text)
      #print text_pos
      for i, (w, pos) in enumerate(text_pos):
        #print w, pos
        if pos[0]=='a' and i > 0 and text_pos[i-1][1][0]=='n':
          text[i] = text_pos[i-1][0]
          text[i-1] = w
          text_pos[i] = text_pos[i-1]
      sys.stdout.write('{}\n'.format(' '.join(text).encode('utf8')))

