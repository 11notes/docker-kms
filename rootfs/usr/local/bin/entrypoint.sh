#!/bin/ash
  if [ -z "${KMS_IP}" ]; then KMS_IP=0.0.0.0; fi
  if [ -z "${KMS_PORT}" ]; then KMS_PORT=1688; fi
  if [ -z "${KMS_LOCALE}" ]; then KMS_LOCALE=1033; fi
  if [ -z "${KMS_ACTIVATIONINTERVAL}" ]; then KMS_ACTIVATIONINTERVAL=120; fi
  if [ -z "${KMS_RENEWALINTERVAL}" ]; then KMS_RENEWALINTERVAL=259200; fi
  if [ -z "${KMS_LOGLEVEL}" ]; then KMS_LOGLEVEL="INFO"; fi

  if [ -z "$1" ]; then
    set -- "python3" \
      /usr/local/bin/py-kms/pykms_Server.py \
      ${KMS_IP} \
      ${KMS_PORT} \
      -l ${KMS_LOCALE} \
      -c 50 \
      -a ${KMS_ACTIVATIONINTERVAL} \
      -r ${KMS_RENEWALINTERVAL} \
      -s /kms/var/kms.db \
      -w RANDOM \
      -V ${KMS_LOGLEVEL} \
      -F /var/log/kms.log \
      -y
  fi

  exec "$@"