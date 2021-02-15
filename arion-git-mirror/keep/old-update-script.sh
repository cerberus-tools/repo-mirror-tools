#!/bin/bash
set -x
folders2=(
"/home/work/git-mirror/git-mirror_home/git/wall.lge.com/webos-pro/bluetooth-sil-rtk.git"
)
for a_folder in "${folders2[@]}"
do
    echo $a_folder
    cd $a_folder
    git config --unset-all remote.origin.fetch
    git config --local --add remote.origin.fetch +refs/heads/*:refs/heads/*
    git config --local --add remote.origin.fetch +refs/tags/*:refs/tags/*
    git config --local --add remote.origin.fetch +refs/changes/*:refs/changes/*
    git remote update --prune
done

folders=(
"/home/work/git-mirror/git-mirror_home/git/wall.lge.com/module"
"/home/work/git-mirror/git-mirror_home/git/wall.lge.com/bsp"
)
for a_folder in "${folders[@]}"
do
    echo $a_folder
    cd $a_folder
    repos=(`find . -name "*.git" -type d|tr '\n' ' '`)
    for a_repo in "${repos[@]}"
    do
        cd $a_repo
        git config --unset-all remote.origin.fetch
        git config --local --add remote.origin.fetch +refs/heads/*:refs/heads/*
        git config --local --add remote.origin.fetch +refs/tags/*:refs/tags/*
        git config --local --add remote.origin.fetch +refs/changes/*:refs/changes/*
        git remote update --prune
        cd $a_folder
    done
done
set +x