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

remt export "$pdf" ~/Desktop/$(basename $pdf).pdf & show_spinner "$!"

echo "Put the file from your desktop to DT, and then copy/paste the dt URL here:"
read dtUrl

if [ -f /tmp/remt_anns.txt ]; then
	rm /tmp/remt_anns.txt
fi

remt index "$pdf" >> /tmp/remt_anns.txt & show_spinner "$!"

python3 from_remt.py $dtUrl
# nvim /tmp/clips.yml

# TODO: prompt for DT url (manual to start), then eventually just export the thing to DT.
# then clip all to hili