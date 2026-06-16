#!/usr/bin/env bash
# Remplace VOTRE_PSEUDO par votre pseudo GitHub dans tout le projet.
# Usage : ./setup.sh mon_pseudo_github
set -e
if [ -z "$1" ]; then
  echo "Usage: ./setup.sh <pseudo_github>"
  exit 1
fi
PSEUDO="$1"
grep -rl "VOTRE_PSEUDO" . --exclude-dir=.git | while read -r f; do
  sed -i "s/VOTRE_PSEUDO/${PSEUDO}/g" "$f"
  echo "maj: $f"
done
echo "Terminé. Pensez à vérifier LICENSE (nom/année) et le README."
