from src.ginsp_lib import *

repo_path = '/home/franz/work/ginsp-sample'
ri = RepoInfo(repo_path)

for b in ri.heads.locals.keys():
    print('  Branch {}'.format(b))
    print(ri.find_release_local(b))

#print(ri.heads.inspect())
#
#mbl = ri.heads.max_local_branch_name_length()
#
#print('------ Consistency Check ------')
#for b1 in ri.heads.locals.keys():
#    for b2 in ri.heads.locals.keys():
#        if b1 == b2:
#            if ri.relations.is_before(b1, b2) or ri.relations.is_after(b1, b2):
#                print("ERROR: Same is before or after")
#        else:
#            if ri.relations.is_before(b1, b2):
#                if ri.relations.is_after(b1, b2):
#                    print("ERROR: is before and after")
#                if not ri.relations.is_after(b2, b1):
#                    print("Error: Wrong inverse:")
#            if ri.relations.is_after(b1, b2):
#                if ri.relations.is_before(b1, b2):
#                    print("ERROR: is after and before")
#                if not ri.relations.is_before(b2, b1):
#                    print("Error: Wrong inverse:")
#            
#print('------ Before / After Relations ------')
#for r in ri.local_relations():
#    a = r[0]
#    b = r[1]
#    if a == b:
#        before = r[2]
#        after = r[3]
#        print("{} {} before {},  {} {} after {}".format(a.ljust(mbl, ' '), '   ' if before else 'not', b.ljust(mbl, ' '), a.ljust(mbl, ' '), '   ' if after else 'not', b.ljust(mbl, ' ')))
#print()
#for r in ri.local_relations():
#    a = r[0]
#    b = r[1]
#    if a != b:
#        before = r[2]
#        after = r[3]
#        print("{} {} before {},  {} {} after {}".format(a.ljust(mbl, ' '), '   ' if before else 'not', b.ljust(mbl, ' '), a.ljust(mbl, ' '), '   ' if after else 'not', b.ljust(mbl, ' ')))
#
