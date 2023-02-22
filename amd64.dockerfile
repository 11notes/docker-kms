# :: Build
  FROM alpine:latest as build

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
    git clone https://github.com/SystemRage/py-kms.git /tmp/py-kms; \
    mv /tmp/py-kms/py-kms /usr/local/bin;

# :: Header
	FROM python:3.7.10-alpine
	COPY --from=build /usr/local/bin/ /usr/local/bin

# :: Run
USER root

# :: prepare
  RUN set -ex; \
    mkdir -p /kms; \
    mkdir -p /kms/var; \
    ln -sf /dev/stdout /var/log/kms.log;

  RUN set -ex; \
    apk add --update --no-cache \
      py3-configargparse \
      py3-flask \
      py3-pygments \
      python3-tkinter \
      sqlite-libs \
      python3-dev \
      sqlite-dev \
      gcc \
      musl-dev \
      py3-pip; \
    pip3 install \
      peewee \
      tzlocal \
      pysqlite3;

  RUN set -ex; \
    addgroup --gid 1000 -S kms; \
    adduser --uid 1000 -D -S -h /kms -s /sbin/nologin -G kms kms;

  # :: copy root filesystem changes
    COPY ./rootfs /

  # :: docker -u 1000:1000 (no root initiative)
    RUN set -ex; \
      chown -R kms:kms \
      /kms

# :: Volumes
	VOLUME ["/kms/var"]

# :: Start
	RUN set -ex; chmod +x /usr/local/bin/entrypoint.sh
	USER kms
	ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]