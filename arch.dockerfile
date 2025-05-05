ARG APP_UID=1000
ARG APP_GID=1000

# :: Util
  FROM 11notes/util AS util

# :: Build / py-kms
  FROM alpine/git AS build
  ARG APP_VERSION
  ARG BUILD_ROOT=/git/fork-py-kms
  RUN set -ex; \
    git clone https://github.com/11notes/fork-py-kms -b next; \
    cd ${BUILD_ROOT}; \
    git checkout v${APP_VERSION}; \
    cp -R ${BUILD_ROOT}/docker/docker-py3-kms-minimal/requirements.txt ${BUILD_ROOT}/py-kms/requirements.txt; \
    cp -R ${BUILD_ROOT}/docker/docker-py3-kms/requirements.txt ${BUILD_ROOT}/py-kms/requirements.gui.txt;

# :: Header
  FROM 11notes/alpine:stable

  # :: arguments
    ARG TARGETARCH
    ARG APP_IMAGE
    ARG APP_NAME
    ARG APP_VERSION
    ARG APP_ROOT
    ARG APP_UID
    ARG APP_GID
    ARG APP_NO_CACHE

    # :: python image
      ARG PIP_ROOT_USER_ACTION=ignore
      ARG PIP_BREAK_SYSTEM_PACKAGES=1
      ARG PIP_DISABLE_PIP_VERSION_CHECK=1
      ARG PIP_NO_CACHE_DIR=1

  # :: environment
    ENV APP_IMAGE=${APP_IMAGE}
    ENV APP_NAME=${APP_NAME}
    ENV APP_VERSION=${APP_VERSION}
    ENV APP_ROOT=${APP_ROOT}

    ENV KMS_LOCALE=1033
    ENV KMS_CLIENTCOUNT=26
    ENV KMS_ACTIVATIONINTERVAL=120
    ENV KMS_RENEWALINTERVAL=259200
    ENV KMS_LOGLEVEL="INFO"

  # :: multi-stage
    COPY --from=util /usr/local/bin /usr/local/bin
    COPY --from=build ${BUILD_ROOT}/py-kms /opt/py-kms

# :: Run
  USER root
  RUN eleven printenv;

  # :: install application
    RUN set -ex; \
      apk --no-cache --update add \
        python3; \
      apk --no-cache --update --virtual .build add \
        py3-pip;

    RUN set -ex; \
      mkdir -p ${APP_ROOT}/var; \
      pip3 install -r /opt/py-kms/requirements.txt; \
      pip3 install pytz; \
      pip3 list -o | sed 's/pip.*//' | grep . | cut -f1 -d' ' | tr " " "\n" | awk '{if(NR>=3)print}' | cut -d' ' -f1 | xargs -n1 pip3 install -U; \
      apk del --no-network .build; \
      rm -rf /usr/lib/python3.12/site-packages/pip;

  # :: copy filesystem changes and set correct permissions
    COPY ./rootfs /
    RUN set -ex; \
      chmod +x -R /usr/local/bin; \
      chown -R ${APP_UID}:${APP_GID} \
        ${APP_ROOT} \
        /opt/py-kms;

  # :: support unraid
    RUN set -ex; \
      eleven unraid

# :: Volumes
  VOLUME ["${APP_ROOT}/var"]

# :: Monitor
  HEALTHCHECK --interval=5s --timeout=2s CMD netstat -an | grep -q 1688 || exit 1

# :: Start
  USER ${APP_UID}:${APP_GID}