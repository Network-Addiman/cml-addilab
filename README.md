# CML Home Lab

# CML Config Backup Tool

A small starter script for the CML lab: it SSHes into my lab devices,
pulls `show running-config`, and drops a timestamped copy into `configs/`.
It doubles as a git-reps machine — every lab change becomes a commit.