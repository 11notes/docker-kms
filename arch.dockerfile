# ╔═════════════════════════════════════════════════════╗
# ║                       SETUP                         ║
# ╚═════════════════════════════════════════════════════╝
  # GLOBAL
  ARG APP_UID=1000 \
      APP_GID=1000 \
      BUILD_SRC=https://github.com/11notes/fork-py-kms.git \
      BUILD_ROOT=/git/fork-py-kms

  # :: FOREIGN IMAGES
  FROM 11notes/util AS util

# ╔═════════════════════════════════════════════════════╗
# ║                       BUILD                         ║
# ╚═════════════════════════════════════════════════════╝
  # :: PY-KMS
  FROM alpine/git AS build
  ARG APP_VERSION \
      BUILD_SRC \
      BUILD_ROOT

  RUN set -ex; \
    git clone ${BUILD_SRC} -b next; \
    cd ${BUILD_ROOT}; \
    git checkout v${APP_VERSION};

  RUN set -ex; \
    cd ${BUILD_ROOT}; \
    cp -R ${BUILD_ROOT}/docker/docker-py3-kms-minimal/requirements.txt ${BUILD_ROOT}/py-kms/requirements.txt; \
    cp -R ${BUILD_ROOT}/docker/docker-py3-kms/requirements.txt ${BUILD_ROOT}/py-kms/requirements.gui.txt;

# ╔═════════════════════════════════════════════════════╗
# ║                       IMAGE                         ║
# ╚═════════════════════════════════════════════════════╝
  # :: HEADER
  FROM 11notes/python:3.13

  # :: default arguments
    ARG TARGETPLATFORM \
        TARGETOS \
        TARGETARCH \
        TARGETVARIANT \
        APP_IMAGE \
        APP_NAME \
        APP_VERSION \
        APP_ROOT \
        APP_UID \
        APP_GID \
        APP_NO_CACHE

  # :: default python image
    ARG PIP_ROOT_USER_ACTION=ignore \
        PIP_BREAK_SYSTEM_PACKAGES=1 \
        PIP_DISABLE_PIP_VERSION_CHECK=1 \
        PIP_NO_CACHE_DIR=1

  # :: image specific arguments
    ARG BUILD_ROOT

  # :: default environment
    ENV APP_IMAGE=${APP_IMAGE} \
        APP_NAME=${APP_NAME} \
        APP_VERSION=${APP_VERSION} \
        APP_ROOT=${APP_ROOT}

  # :: app specific variables
    ENV KMS_LOCALE=1033 \
        KMS_ACTIVATIONINTERVAL=120 \
        KMS_RENEWALINTERVAL=259200

  # :: multi-stage
    COPY --from=util /usr/local/bin /usr/local/bin
    COPY --from=build ${BUILD_ROOT}/py-kms /opt/py-kms

# :: RUN
  USER root

  # :: install dependencies
    RUN set -ex; \
      apk --no-cache --update --virtual .build add \
        py3-pip;

  # :: install and update application
    RUN set -ex; \
      mkdir -p ${APP_ROOT}/var; \
      pip3 install -r /opt/py-kms/requirements.txt; \
      pip3 install pytz; \
      pip3 list -o | sed 's/pip.*//' | grep . | cut -f1 -d' ' | tr " " "\n" | awk '{if(NR>=3)print}' | cut -d' ' -f1 | xargs -n1 pip3 install -U; \
      apk del --no-network .build; \
      rm -rf /usr/lib/python3.13/site-packages/pip;

  # :: copy root filesystem and set correct permissions
    COPY ./rootfs /
    RUN set -ex; \
      chmod +x -R /usr/local/bin; \
      chown -R ${APP_UID}:${APP_GID} \
        ${APP_ROOT} \
        /opt/py-kms;

  # :: enable unraid support
    RUN set -ex; \
      eleven unraid

# :: PERSISTENT DATA
  VOLUME ["${APP_ROOT}/var"]

# :: HEALTH
  HEALTHCHECK --interval=5s --timeout=2s --start-interval=5s \
    CMD ["/usr/bin/nc", "-z", "localhost", "1688"]

# :: EXECUTE
  USER ${APP_UID}:${APP_GID}
  ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/entrypoint.sh"]