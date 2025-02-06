#!/bin/ash
  if [ -z "${1}" ]; then
    eleven log start
    set -- "pykms_Server" \
      ${KMS_IP} \
      ${KMS_PORT} \
      -l ${KMS_LOCALE} \
      -c ${KMS_CLIENTCOUNT} \
      -a ${KMS_ACTIVATIONINTERVAL} \
      -r ${KMS_RENEWALINTERVAL} \
      -s /kms/var/kms.db \
      -w RANDOM \
      -V ${KMS_LOGLEVEL} \
      -F /var/log/kms.log \
      -d \
      -y
  fi

  exec "$@"