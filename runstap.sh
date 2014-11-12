#!/bin/bash

set -eu

run_with_echo() {
  echo 1>&2 "$@"
  echo 1>&2
  "$@"
}

OUT="example.txt"
if [ $# -eq 1 ]; then
  OUT="$1"
fi

echo "going to run stap with output to: $OUT"
echo
run_with_echo stap -DMAXACTION=10000 -DSTP_NO_OVERLOAD -I /usr/share/doc/systemtap-client/examples/general/tapset -v /usr/share/doc/systemtap-client/examples/general/py2example.stp -c "python timeout_example.py" > "$OUT"
