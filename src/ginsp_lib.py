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

class MapOfSet:
    def __init__(self):
        self.map = {}
    
    def __getitem__(self, key):
        if key not in self.map:
            self.map[key] = set()
        return self.map[key]

    def keys(self):
        return self.map.keys()

    def items(self):
        return self.map.items()

    def __repr__(self):
        return "MapOfSet{}".format(self.map)

class Commit:
    def __init__(self, repo, sha1):
        self.repo = repo
        self.sha1 = sha1
        self.parents = None
        self.release_candidates = set()
        self.terminators = set()
        self.later_releases = set()

    def get_parents(self):
        if self.parents is None:
            self.parents = []
            for l in cmd("git cat-file -p {}".format(self.sha1)).splitlines():
                if l.startswith("parent "):
                    parent_sha1 = l.split("parent ")[1]
                    self.parents.append(self.repo.get_commit(parent_sha1))
        return self.parents

class GitRepo:
    def __init__(self, repo_path, remote):
        os.chdir(repo_path)
        cmd('git fetch {} -t --prune'.format(remote))

        self.commits_by_sha1 = {}

        self.release_names = set()

        # heads: key = tag/branch, value = sha1 of commit
        self.heads = {}
        branch_prefix = 'refs/remotes/{}/'.format(remote)
        tag_prefix = 'refs/tags/'
        for l in cmd('git show-ref').splitlines():
            sha1, ref = l.split(' ')
            if ref.startswith(branch_prefix):
                self.heads[ref.split(branch_prefix)[1]] = sha1
            elif ref.startswith(tag_prefix):
                self.heads[ref.split(tag_prefix)[1]] = sha1

        terminated_releases = set()
        terminators = []
        for name, sha1 in self.heads.items():
            if name.startswith('golive/'):
                release = name.split('golive/')[1]
                terminators.append( (release,sha1))
                c = self.get_commit(sha1)
                c.terminators.add(release)
                terminated_releases.add(release)

        for name, sha1 in self.heads.items():
            if name.startswith('golive/'):
                self._spread_release(name.split('golive/')[1], sha1)
        for head, sha1 in self.heads.items():
            if head.startswith('dev/'):
                self._spread_release(head.split('dev/')[1].split('.')[0], sha1)
            elif name.startswith('release/'):
                self._spread_release(head.split('release/')[1], sha1)
            elif name.startswith('pre/'):
                self._spread_release(head.split('pre/')[1], sha1)

    def _spread_release(self, release, sha1):
        if release not in self.release_names:
            self.release_names.add(release)
        commit = self.get_commit(sha1)
        if len(commit.terminators) == 0 or release in commit.terminators:
            commit.release_candidates.add(release)
            for p in commit.get_parents():
                self._spread_release(release, p.sha1)
        else:
            commit.later_releases.add(release)

    def get_commit(self, sha1):
        if sha1 in self.commits_by_sha1:
            return self.commits_by_sha1[sha1]
        else:
            c = Commit(self, sha1)
            self.commits_by_sha1[sha1] = c
            return c

    def _find_release_candidates(self, cand, commit):
        if len(commit.terminators) > 0:
            cand.update(commit.later_releases)
        elif len(commit.release_candidates) > 0:
            cand.update(commit.release_candidates)
        else:
            for p in commit.get_parents():
                self._find_release_candidates(cand, p)

    def get_release(self, feature_branch):
        sha1 = self.heads[feature_branch]
        commit = self.get_commit(sha1)
        release_candidates = set()
        self._find_release_candidates(release_candidates, commit)
        if len(release_candidates) == 1:
            return list(release_candidates)[0]
        else:
            print("Can't tell release of {} from looking at Git, have to check Jira ({})".format(feature_branch, ", ".join(list(release_candidates))))
            return None

    def branches(self):
        return self.heads.keys()

    def feature_branches(self):
        return [b for b in self.heads.keys() if b.startswith('feature/')]

    def releases(self):
        return sorted(list(self.release_names))

