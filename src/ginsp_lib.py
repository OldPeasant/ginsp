import os
import subprocess

def cmd(cmds):
    proc = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=True)
    proc.wait()
    out, err = proc.communicate()
    if err:
        logging.error(err)
        raise Exception("Failed to run '{}'".format(cmd))
    return out.decode("utf8")

PREFIX_LOCAL = 'refs/heads/'
PREFIX_REMOTE = 'refs/remotes/'

class MapOfSet:
    def __init__(self):
        self.map = {}
    
    def __getitem__(self, key):
        if key not in self.map:
            self.map[key] = set()
        return self.map[key]

    def keys(self):
        return self.map.keys()

    def __repr__(self):
        return "MapOfSet{}".format(self.map)

class Heads():
    def __init__(self):
        self.locals = {}
        self.remotes = {}
        for l in cmd('git show-ref').splitlines():
            sha1, ref = l.split(' ')
            if ref.startswith(PREFIX_LOCAL):
                self.locals[ref[len(PREFIX_LOCAL):]] = sha1
            elif ref.startswith('refs/remotes/'):
                remote, branch = ref[len(PREFIX_REMOTE):].split('/')
                self._add_remote(remote, branch, sha1)

    def branch_names(self):
        all = set()
        all.update(self.locals.keys())
        for r in self.remotes.keys():
            all.update(self.remotes[r].keys())
        return all

    def max_local_branch_name_length(self):
        return max([len(b) for b in self.locals.keys()])

    def _add_remote(self, remote, branch, sha1):
        if remote not in self.remotes:
            self.remotes[remote] = {}
        self.remotes[remote][branch] = sha1

    def inspect(self):
        lines = []
        lines.append("CommitNet[")
        lines.append("  Local:")
        for l in sorted(self.locals.keys()):
            lines.append("    {} : {}".format(l, self.locals[l][:8]))
        lines.append("  Remote:")
        for r in sorted(self.remotes.keys()):
            lines.append("    {}".format(r))
            rb = self.remotes[r]
            for b in sorted(rb.keys()):
                lines.append("      {} : {}".format(b, rb[b][:8]))
        lines.append(']')
        return '\n'.join(lines)


class RevLists:
    def __init__(self):
        self.data = {}
    def get(self, sha1):
        if sha1 not in self.data:
            self.data[sha1] = cmd('git rev-list {}'.format(sha1)).splitlines()
        return self.data[sha1]

class RelKey:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def inv(self):
        return RelKey(self.b, self.a)

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def __hash__(self):
        return hash((self.a, self.b))

    def __repr__(self):
        return 'RelKey[{}, {}]'.format(self.a[:8], self.b[:8])

class Relations:
    def __init__(self, rev_lists):
        self.rev_lists = rev_lists
        self.before = {}
        self.after = {}
    
    def is_before(self, a, b):
        if a == b:
            return False
        return self.before[self._key(a, b)]

    def is_after(self, a, b):
        if a == b:
            return False
        return self.after[self._key(a, b)]

    def _key(self, a, b):
        k = RelKey(a, b)
        if k not in self.before:
            if k in self.after:
                raise Exception('Nasty inconsistency (1): {}'.format(k))
            self._calc(k)
        if k not in self.after:
            raise Exception('Nasty inconsistency (2): {}'.format(k))
        return k

    def _calc(self, key):
        inv = key.inv()
        found1 = False
        for anc in self.rev_lists.get(key.a):
            if key.b == anc:
                self.after[key] = True
                self.after[inv] = False
                self.before[key] = False
                self.before[inv] = True
                found1 = True
                break

        found2 = False
        for anc in self.rev_lists.get(key.b):
            if key.a == anc:
                if key in self.before or key in self.after:
                    raise Exception("Nasty inconsistency (3) {}".format(key))
                self.after[key] = True
                self.after[inv] = False
                self.before[key] = False
                self.before[inv] = True
                found2 = True
                break
        if not found1 and not found2:
            self.after[key] = False
            self.after[inv] = False
            self.before[key] = False
            self.before[inv] = False

class RepoInfo:
    def __init__(self, path):
        os.chdir(path)
        for r in cmd('git remote').splitlines():
            cmd('git fetch {}'.format(r))
        self.heads = Heads()
        self.rev_lists = RevLists()
        self.relations = Relations(self.rev_lists)

    def local_relations(self):
        result = []
        for h1 in sorted(self.heads.locals.keys()):
            h1_sha1 = self.heads.locals.get(h1)
            for h2 in sorted(self.heads.locals.keys()):
                h2_sha1 = self.heads.locals.get(h2)
                result.append((h1, h2, self.relations.is_before(h1_sha1, h2_sha1), self.relations.is_after(h1_sha1, h2_sha1)))
        return result

    def _find_release_commits(self, heads_map):
        release_prefix = 'release/'
        dev_prefix = 'dev/'
        release_candidates = MapOfSet()
        for b in heads_map.keys():
            if b.startswith(release_prefix):
                release_name = b[len(release_prefix):]
                release_candidates[release_name].add(heads_map[b])
            if b.startswith(dev_prefix):
                dev_branch_name = b[len(dev_prefix):]
                release_name = dev_branch_name.split('.')[0]
                release_candidates[release_name].add(heads_map[b])
        return release_candidates

    def _find_release(self, heads_map, branch_name):
        release_commits = self._find_release_commits(heads_map)
        branch_sha1 = heads_map[branch_name]
        

        
    def find_release_local(self, branch_name):
        h = self.heads.locals
        return self._find_release(self.heads.locals, branch_name)

    def find_release_remote(self, remote, branch_name):
        return self._find_release(self.heads.remotes[remote], branch_name)
        
