# ╔═════════════════════════════════════════════════════╗
# ║                       SETUP                         ║
# ╚═════════════════════════════════════════════════════╝
# GLOBAL
  ARG APP_UID=1000 \
      APP_GID=1000 \
      APP_PYTHON_VERSION=0

# :: FOREIGN IMAGES
  FROM 11notes/util:bin AS util-bin
  FROM 11notes/util AS util
  FROM 11notes/distroless:nc AS distroless-nc
  FROM 11notes/distroless:tini AS distroless-tini


# ╔═════════════════════════════════════════════════════╗
# ║                       BUILD                         ║
# ╚═════════════════════════════════════════════════════╝
# :: SOURCE
  FROM alpine/git AS source
  COPY --from=util-bin / /
  ARG APP_VERSION

  RUN set -ex; \
    eleven git clone 11notes/fork-py-kms.git v${APP_VERSION};

# :: KMS
  FROM 11notes/python:${APP_PYTHON_VERSION} AS build
  COPY --from=source /git/fork-py-kms/py-kms /opt/py-kms
  ARG APP_VERSION
  USER root

  RUN set -ex; \
    pip install \
      uv;

  RUN set -ex; \
    uv pip install \
      --only-binary=:all: \
      -r https://raw.githubusercontent.com/11notes/fork-py-kms/refs/tags/v${APP_VERSION}/docker/docker-py3-kms-minimal/requirements.txt \
      pytz;

# :: FILE-SYSTEM
  FROM alpine AS file-system
  ARG APP_ROOT \
      APP_UID \
      APP_GID
  COPY ./rootfs/ /distroless/

  RUN set -ex; \
    mkdir -p /distroless${APP_ROOT}/var; \
    mkdir -p /distroless/opt/py-kms;

  RUN set -ex; \
    chown -R ${APP_UID}:${APP_GID} \
      /distroless${APP_ROOT};

  RUN set -ex; \
    chmod +x -R /distroless/usr/local/bin;


# ╔═════════════════════════════════════════════════════╗
# ║                       IMAGE                         ║
# ╚═════════════════════════════════════════════════════╝
# :: HEADER
  FROM scratch

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
    COPY --from=distroless-nc / /
    COPY --from=distroless-tini / /
    COPY --from=util / /
    COPY --from=build / /
    COPY --from=file-system /distroless/ /

# :: PERSISTENT DATA
  VOLUME ["${APP_ROOT}/var"]

# :: MONITORING
  HEALTHCHECK --interval=5s --timeout=2s --start-period=5s \
    CMD ["/usr/local/bin/nc", "-z", "localhost", "1688"]

# :: EXECUTE
  USER ${APP_UID}:${APP_GID}
  ENTRYPOINT ["/usr/local/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]