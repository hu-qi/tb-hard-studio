#!/usr/bin/env bash
set -u
mkdir -p /logs/verifier

# TODO: run independent behavior-based verification.
echo 0 > /logs/verifier/reward.txt
exit 1
