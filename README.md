# Alpine:: Python KMS
Run a KMS server based on Alpine Linux. Small, lightweight, secure and fast 🏔️

## Volumes
* **/kms/var** - Directory of the sqlite database

## Run
```shell
docker run --name kms \
  -v ../var:/kms/var \
  -d 11notes/kms:[tag]
```

## Defaults
| Parameter | Value | Description |
| --- | --- | --- |
| `user` | docker | user docker |
| `uid` | 1000 | user id 1000 |
| `gid` | 1000 | group id 1000 |
| `home` | /kms | home directory of user docker |

## Environment
| Parameter | Value | Default |
| --- | --- | --- |
| `KMS_IP` | localhost or 127.0.0.1 or a dedicated IP | 0.0.0.0 |
| `KMS_PORT` | any port > 1024 | 1688 |
| `KMS_LOCALE` | see Microsoft LICD specification | 1033 (en-US) |
| `KMS_ACTIVATIONINTERVAL` | Retry unsuccessful after N minutes | 120 (2 hours) |
| `KMS_RENEWALINTERVAL` | re-activation after N minutes | 259200 (180 days) |
| `KMS_LOGLEVEL` | CRITICAL, ERROR, WARNING, INFO, DEBUG, MININFO | INFO |

## Parent
* [python:3.7.10-alpine](https://hub.docker.com/layers/library/python/3.7.10-alpine/images/sha256-932f7a8769b07d1effc5a46cb1463948542a017e82350c93f56792bec08ff9dd?context=explore)

## Built with
* [py-kms](https://github.com/Py-KMS-Organization/py-kms)
* [Alpine Linux](https://alpinelinux.org/)

## Tips
* Don't bind to ports < 1024 (requires root), use NAT/reverse proxy
* [Persistent Storage](https://github.com/11notes/alpine-docker-netshare)
* [Microsoft LICD](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/6c085406-a698-4e12-9d4d-c3b0ee3dbc4a)