#!/usr/bin/env bash

show_spinner()
{
  local -r pid="${1}"
  local -r delay='0.75'
  local spinstr='\|/-'
  local temp
  while ps a | awk '{print $1}' | grep -q "${pid}"; do
    temp="${spinstr#?}"
    printf " [%c]  " "${spinstr}"
    spinstr=${temp}${spinstr%"${temp}"}
    sleep "${delay}"
    printf "\b\b\b\b\b\b"
  done
  printf "    \b\b\b\b"
}

eval "$(conda shell.bash hook)"
conda activate remarkable-layers

echo "Enter the name of the file on your remarkable:"
read pdf

# TODO: test remarkable is plugged in, IP address correct, etc.

rm /tmp/remt_anns.txt
remt index "$pdf" >> /tmp/remt_anns.txt & show_spinner "$!"

python from_remt.py
nvim /tmp/clips.yml

# TODO: prompt for DT url (manual to start), then eventually just export the thing to DT.
# then clip all to hili
