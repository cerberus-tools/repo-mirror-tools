#!/usr/bin/env python

import sys, os, subprocess, re, traceback
import json
from multiprocessing import Pool, Process, Queue, Array, Manager
import time

git_host = os.environ['GIT_HOST']
git_base_dir = os.environ['GIT_BASE_DIR']
git_home = git_base_dir + os.sep + git_host


def check_out(x, y):
    while True:
        try:
            project_name = x.pop()
            git_url = "ssh://{}/{}".format(git_host, project_name)
            sys.stderr.write("INFO:" + project_name + "\n")
            try:
                check_project = y[project_name]
            except:
                check_project = False
                y[project_name] = False
            sys.stderr.write("INFO:Check_project:" + str(check_project) + "\n")
            if check_project:
                x.append(project_name)
            else:
                sys.stderr.write("INFO:Start_process\n")
                y[project_name] = True
                git_repo_dir = git_home + os.sep + project_name + ".git"
                start_t = time.time()
                result = os.system("cd {} && git remote update --prune".format(git_repo_dir))
                end_t = time.time()
                sys.stderr.write(
                    "TIME: {} - {}\n".format(git_repo_dir, str(end_t - start_t))
                )
                if not result == 0:
                    sys.stderr.write("Error : {}".format(git_repo_dir) + "\n")
                    sys.stderr.write("INFO : Remove {} and download it again".format(git_repo_dir) + "\n")
                    os.system("rm -rf {}".format(git_repo_dir))
                    sys.stderr.write("git clone --mirror {} {}\n".format(git_url, git_repo_dir))
                    os.system("git clone --mirror {} {}".format(git_url, git_repo_dir))
                    os.system("cd {} && git config --unset-all remote.origin.fetch".format(git_repo_dir))
                    os.system("cd {} && git config --local --add remote.origin.fetch +refs/heads/*:refs/heads/*".format(
                        git_repo_dir))
                    os.system("cd {} && git config --local --add remote.origin.fetch +refs/tags/*:refs/tags/*".format(
                        git_repo_dir))
                    os.system(
                        "cd {} && git config --local --add remote.origin.fetch +refs/changes/*:refs/changes/*".format(
                            git_repo_dir))
                y[project_name] = False
            time.sleep(2)
        except IndexError:
            time.sleep(2)
        except IOError:
            traceback.print_exc()
            sys.stderr.write("INFO: waiting_queue size = " + str(len(x)))
            time.sleep(2)
    return


gerrit_stream = subprocess.Popen(['ssh', git_host, 'gerrit', 'stream-events'], stdout=subprocess.PIPE).stdout

manager = Manager()
waiting_queue = manager.list()
inprogress_dict = manager.dict()

list_of_process = []
# Generate a list of processes that handle each repo's updating command
# waiting_queue: List of projects to be updated
# inprogress_dict: List of projects being updated
for i in range(4):
    list_of_process.append(Process(target=check_out, args=(waiting_queue, inprogress_dict,)))
    list_of_process[i].start()

while True:
    each_line = gerrit_stream.readline()
    sys.stderr.write("CHECK: project catch : {}".format(each_line))
    try:
        # Change each_line to json data type
        change_data = json.loads(each_line)
    except:
        print("ERROR: When converting change json string to json data")
        print("ERROR: each_line: %s " % each_line)
        for j in range(4):
            list_of_process[i].terminate()
        import sys

        sys.exit(1)
    # Add a project to candidates to be updated when one of 'patchset-created', 'change-merged', 'ref-updated'
    if change_data['type'] == 'patchset-created' or change_data['type'] == 'change-merged':
        project_name = change_data['change']['project']
        branch = change_data['change']['branch']
        change_number = change_data['change']['number']
    elif change_data['type'] == 'ref-updated':
        project_name = change_data['refUpdate']['project']
    else:
        continue
    if not project_name in waiting_queue and not re.compile(
            '.*restricted.*|.*buildhistory.*|.*z-parent.*|.*oe-build-analysis.*').match(project_name):
        waiting_queue.append(project_name)
