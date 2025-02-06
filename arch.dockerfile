# :: Util
  FROM alpine AS util

  RUN set -ex; \
    apk --no-cache --update add \
      git; \
    git clone https://github.com/11notes/docker-util.git;

# :: Build / redis
  FROM python:3.12-alpine AS build

  ARG TARGETARCH
  ARG APP_VERSION

  USER root

  RUN set -ex; \
    apk --update --no-cache add \
      curl \
      wget \
      unzip \
      build-base \
      linux-headers \ 
      make \
      cmake \
      g++ \
      git; \
    pip3 install --upgrade pip; \
    pip3 install pyinstaller; \
    git clone https://github.com/Py-KMS-Organization/py-kms.git; \
    cd /py-kms/py-kms; \
    git checkout ${APP_VERSION}; \
    pyinstaller --onefile pykms_Server.py; \
    cp /py-kms/py-kms/dist/pykms_Server /usr/local/bin;

# :: Header
  FROM 11notes/alpine:stable

  # :: arguments
    ARG TARGETARCH
    ARG APP_IMAGE
    ARG APP_NAME
    ARG APP_VERSION
    ARG APP_ROOT

  # :: environment
    ENV APP_IMAGE=${APP_IMAGE}
    ENV APP_NAME=${APP_NAME}
    ENV APP_VERSION=${APP_VERSION}
    ENV APP_ROOT=${APP_ROOT}

    ENV KMS_IP=0.0.0.0
    ENV KMS_PORT=1688
    ENV KMS_LOCALE=1033
    ENV KMS_CLIENTCOUNT=25
    ENV KMS_ACTIVATIONINTERVAL=120
    ENV KMS_RENEWALINTERVAL=259200
    ENV KMS_LOGLEVEL="INFO"

  # :: multi-stage
    COPY --from=util /docker-util/src/ /usr/local/bin
    COPY --from=build /usr/local/bin/ /usr/local/bin

  # :: Run
  USER root

  # :: install application
    RUN set -ex; \
      apk --no-cache --update add \
        python3;

    RUN set -ex; \
      mkdir -p ${APP_ROOT}/var; \
      touch /var/log/kms.log; \
      ln -sf /dev/stdout /var/log/kms.log;

  # :: copy filesystem changes and set correct permissions
    COPY ./rootfs /
    RUN set -ex; \
      chmod +x -R /usr/local/bin; \
      chown -R 1000:1000 \
        ${APP_ROOT};

# :: Volumes
  VOLUME ["${APP_ROOT}/var"]

# :: Monitor
  HEALTHCHECK --interval=5s --timeout=2s CMD /usr/local/bin/healthcheck.sh || exit 1

# :: Start
  USER docker