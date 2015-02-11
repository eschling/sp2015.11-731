import sys

def main(forward_file, backward_file):
  fw_f = open(forward_file)
  bw_f = open(backward_file)
  fw = fw_f.read().split('\n')
  bw = bw_f.read().split('\n')
  assert(len(bw)==len(fw))
  for i in range(len(fw)):
    fw_align = set(fw[i].strip().split())
    bw_align = set()
    len_e = 0
    len_f = 0
    for al in bw[i].strip().split():
      f, e = al.split('-')
      bw_align.add('{}-{}'.format(e, f))
    intersection = fw_align & bw_align
    aligned_e = set()
    aligned_f = set()
    for al in intersection:
      e, f = al.split('-')
      if int(e) > len_e: len_e = int(e)
      if int(f) > len_f: len_f = int(e)
      aligned_e.add(e)
      aligned_f.add(f)
    len_e += 1
    len_f += 1
    union = fw_align | bw_align
    alignment, aligned_e, aligned_f = grow_diag(intersection, union, aligned_e,
                                                aligned_f, len_e, len_f)
    #final_fw = final_and(fw_align, aligned_e, aligned_f, len_e, len_f)
    #final_bw = final_and(bw_align, aligned_e, aligned_f, len_e, len_f)
    #symmetrized = alignment | final_fw | final_bw
    symm = sorted(list(alignment), key=lambda al: int(al.split('-')[0]))
    print ' '.join(symm)

def grow_diag(intersection, union, aligned_e, aligned_f, len_e, len_f):
  align = set()
  while True:
    for i in range(len_e):
      for j in range(len_f):
        if '{}-{}'.format(i,j) in intersection:
          neighbors = ((i-1,j-1), (i-1, j), (i-1, j+1), (i, j-1),
                      (i, j+1), (i+1, j-1), (i+1, j), (i+1, j+1))
          for e, f in neighbors:
            if e==len_e or f==len_f or e < 0 or f < 0: continue
            new = '{}-{}'.format(e,f)
            if ((e not in aligned_e) or (f not in aligned_f)) and new in union:
              align.add(new)
              aligned_e.add(e)
              aligned_f.add(f)
            
    intersection = intersection | align
    if len(align)==0: break
    align = set()
  return intersection, aligned_e, aligned_f

def final_and(a, aligned_e, aligned_f, len_e, len_f):
  align = set()
  for i in range(len_e+1):
    for j in range(len_f+1):
      new = '{}-{}'.format(i,j)
      if ((i not in aligned_e) and (j not in aligned_f)) and new in a:
        align.add(new)
  return align

if __name__=='__main__':
  main(sys.argv[1], sys.argv[2])
