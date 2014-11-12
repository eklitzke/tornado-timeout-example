#!/bin/bash

OUT="example.txt"
echo "going to run stap with output to $OUT"
echo
set -eux
stap -DMAXACTION=10000 -DSTP_NO_OVERLOAD -I /usr/share/doc/systemtap-client/examples/general/tapset -v /usr/share/doc/systemtap-client/examples/general/py2example.stp -c "python timeout_example.py" > "$OUT"

set +x
echo
echo "get stap output with:"
echo "less $OUT"
