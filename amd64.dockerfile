# :: Build
  FROM alpine as build

  RUN set -ex; \
    apk add --update --no-cache \
      curl \
      wget \
      unzip \
      build-base \
      linux-headers \ 
      make \
      cmake \
      g++ \
      git; \
    git clone https://github.com/Py-KMS-Organization/py-kms.git /tmp/py-kms; \
    mv /tmp/py-kms/py-kms /usr/local/bin;

# :: Header
  FROM python:3.11-alpine
  COPY --from=build /usr/local/bin/ /usr/local/bin
  ENV APP_ROOT=/kms
  ENV APP_NAME="kms"
  ENV APP_VERSION="latest"
  ENV KMS_IP=0.0.0.0
  ENV KMS_PORT=1688
  ENV KMS_LOCALE=1033
  ENV KMS_CLIENTCOUNT=25
  ENV KMS_ACTIVATIONINTERVAL=120
  ENV KMS_RENEWALINTERVAL=259200
  ENV KMS_LOGLEVEL="INFO"

# :: Run
  USER root

  # :: update image
    RUN set -ex; \
      apk --no-cache --update add \
        curl \
        tzdata \
        shadow; \
      apk --no-cache upgrade;

  # :: prepare image
    RUN set -ex; \
      mkdir -p ${APP_ROOT}; \
      mkdir -p ${APP_ROOT}/var; \
      touch /var/log/kms.log; \
      ln -sf /dev/stdout /var/log/kms.log;

    RUN set -ex; \
      apk add --no-cache \
        py3-configargparse \
        py3-pygments \
        python3-tkinter \
        sqlite-libs \
        python3-dev \
        sqlite-dev \
        gcc \
        musl-dev \
        py3-pip; \
      pip3 install --no-cache-dir \
        peewee \
        tzlocal \
        pytz \
        pysqlite3;

    # :: create user
      RUN set -ex; \
        addgroup --gid 1000 -S docker; \
        adduser --uid 1000 -D -S -h / -s /sbin/nologin -G docker docker;

    # :: copy root filesystem changes and set correct permissions
      COPY ./rootfs /
      RUN set -ex; \
        chmod +x -R /usr/local/bin; \
        usermod -d ${APP_ROOT} docker; \
        chown -R 1000:1000 \
          ${APP_ROOT} \
          /var/log/kms.log;

# :: Volumes
  VOLUME ["${APP_ROOT}/var"]

# :: Start
  USER docker
  ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]