#!/usr/bin/python3

from src.ginsp_lib import *

repo_path = '../sample-repo-local'
remote = 'origin'


repo = GitRepo(repo_path, remote)

print("===== Repo Info for remote {} =====".format(remote))
print("----- Branches -----")
for b in repo.branches():
    print('  Branch {}'.format(b))
print("----- Releases -----")
for r in repo.releases():
    print('  Release {}'.format(r))
print("----- Feature Branches -----")
for f in repo.feature_branches():
    print('  Feature Branch {} in release {}'.format(f, repo.get_release(f)))
print("----- The End -----")

print("===== INSPECTION =====")
for sha1, commit in repo.commits_by_sha1.items():
    print("{} : {} / {}".format(
        sha1,
        ", ".join(list(commit.terminators)),
        ", ".join(list(commit.release_candidates))
    ))
