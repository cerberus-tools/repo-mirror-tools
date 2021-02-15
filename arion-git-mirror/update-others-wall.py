from multiprocessing import Pool
import argparse
import glob
import subprocess
from datetime import datetime

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--repo-local-root", default="/home/work/git-mirror/git-mirror_home/git/wall.lge.com/")
args = arg_parser.parse_args()
repo_local_root = args.repo_local_root


def find_git_repo_dirs(root_dir):
    repo_dirs = []
    for dir_path in glob.glob(f"{root_dir}/*.git/", recursive=True):
        repo_dirs.append(dir_path)
    return repo_dirs


def update_mirrored_repo(repo_dir):
    try:
        subprocess.check_call("git ls-remote ", shell=True, cwd=repo_dir, stderr=subprocess.DEVNULL,
                                           stdout=subprocess.DEVNULL)
        print(f"SUCCESS: Can update {repo_dir}")
        subprocess.check_call("git config --unset-all remote.origin.fetch", shell=True, cwd=repo_dir,
                              stderr=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL)
        subprocess.check_call("git config --local --add remote.origin.fetch +refs/heads/*:refs/heads/*", shell=True,
                              cwd=repo_dir,
                              stderr=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL)
        subprocess.check_call("git config --local --add remote.origin.fetch +refs/tags/*:refs/tags/*", shell=True,
                              cwd=repo_dir,
                              stderr=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL)
        subprocess.check_call("git config --local --add remote.origin.fetch +refs/changes/*:refs/changes/*", shell=True,
                              cwd=repo_dir,
                              stderr=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL)
        subprocess.check_call("git remote update --prune", shell=True, cwd=repo_dir,
                                             stderr=subprocess.DEVNULL,
                                             stdout=subprocess.DEVNULL)
        print(f"SUCCESS: updating {repo_dir} is done")
    except subprocess.CalledProcessError as err:
        print(f"ERROR: Command {err.cmd} on {repo_dir} with error code {err.returncode}")


def update_wall_bsp_module():
    sub_folders = (
        "module",
        "bsp"
    )
    folders = map(lambda sub_folder: repo_local_root + sub_folder, sub_folders)
    for each_folder in folders:
        repo_dirs = find_git_repo_dirs(each_folder)
        pool = Pool(4)
        pool.map(update_mirrored_repo, repo_dirs)
        pool.close()
        pool.join()


if __name__ == "__main__":
    before = datetime.now()
    update_wall_bsp_module()
    after = datetime.now()
    print(f"Elapsed time: {after - before}")
