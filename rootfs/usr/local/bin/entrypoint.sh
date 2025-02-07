#!/bin/ash
  if [ -z "${1}" ]; then
    cd /opt/py-kms
    set -- "python3" \
      pykms_Server.py \
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
      -y
    
    eleven log start
  fi

  exec "$@"