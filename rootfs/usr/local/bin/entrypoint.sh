#!/bin/ash
  if [ -z "${1}" ]; then

    if [ ! -z "${DEBUG}" ]; then
      KMS_LOGLEVEL="DEBUG"
      eleven log debug "setting kms log level to DEBUG"
    fi

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
      -F STDOUT \
      -y
    
    eleven log start
  fi

  exec "$@"