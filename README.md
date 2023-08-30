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

## Parent
* [python:3.7.10-alpine](https://hub.docker.com/layers/library/python/3.7.10-alpine/images/sha256-932f7a8769b07d1effc5a46cb1463948542a017e82350c93f56792bec08ff9dd?context=explore)

## Built with
* [py-kms](https://github.com/Py-KMS-Organization/py-kms)
* [Alpine Linux](https://alpinelinux.org/)

## Tips
* Don't bind to ports < 1024 (requires root), use NAT/reverse proxy
* [Permanent Stroage](https://github.com/11notes/alpine-docker-netshare) - Module to store permanent container data via NFS/CIFS and more