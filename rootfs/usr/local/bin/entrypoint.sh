#!/bin/ash
  if [ -z "$1" ]; then
    set -- "python3" \
      /usr/local/bin/py-kms/pykms_Server.py \
      0.0.0.0 \
      1688 \
      -l 1033 \
      -c 26 \
      -a 120 \
      -r 10080 \
      -s /kms/var/kms.db \
      -w RANDOM \
      -V WARNING \
      -F /var/log/kms.log
  fi

  exec "$@"