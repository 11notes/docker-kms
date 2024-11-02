#!/bin/ash
  if [ -z "${1}" ]; then
    elevenLogJSON info "starting ${APP_NAME}"
    set -- "python3" \
      /usr/local/bin/py-kms/pykms_Server.py \
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
  fi

  exec "$@"