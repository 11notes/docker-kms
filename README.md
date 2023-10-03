# Alpine :: KMS
![size](https://img.shields.io/docker/image-size/11notes/kms/2022.12.16?color=0eb305) ![version](https://img.shields.io/docker/v/11notes/kms?color=eb7a09) ![pulls](https://img.shields.io/docker/pulls/11notes/kms?color=2b75d6) ![activity](https://img.shields.io/github/commit-activity/m/11notes/docker-kms?color=c91cb8) ![commit-last](https://img.shields.io/github/last-commit/11notes/docker-kms?color=c91cb8)


Run a KMS server based on Alpine Linux. Small, lightweight, secure and fast 🏔️

Works with:
- Windows Vista 
- Windows 7 
- Windows 8
- Windows 8.1
- Windows 10 ( 1511 / 1607 / 1703 / 1709 / 1803 / 1809 )
- Windows 10 ( 1903 / 1909 / 20H1, 20H2, 21H1, 21H2 )
- Windows 11 ( 21H2 )
- Windows Server 2008
- Windows Server 2008 R2
- Windows Server 2012
- Windows Server 2012 R2
- Windows Server 2016
- Windows Server 2019
- Windows Server 2022
- Microsoft Office 2010 ( Volume License )
- Microsoft Office 2013 ( Volume License )
- Microsoft Office 2016 ( Volume License )
- Microsoft Office 2019 ( Volume License )
- Microsoft Office 2021 ( Volume License )

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
| `database` | /kms/var/kms.db | SQlite database holding all client data |

## Environment
| Parameter | Value | Default |
| --- | --- | --- |
| `KMS_IP` | localhost or 127.0.0.1 or a dedicated IP | 0.0.0.0 |
| `KMS_PORT` | any port > 1024 | 1688 |
| `KMS_LOCALE` | see Microsoft LICD specification | 1033 (en-US) |
| `KMS_CLIENTCOUNT` | client count >= 25 | 256 |
| `KMS_ACTIVATIONINTERVAL` | Retry unsuccessful after N minutes | 120 (2 hours) |
| `KMS_RENEWALINTERVAL` | re-activation after N minutes | 259200 (180 days) |
| `KMS_LOGLEVEL` | CRITICAL, ERROR, WARNING, INFO, DEBUG, MININFO | INFO |

## Example
Windows Server 2022 Datacenter. List of [GVLK](https://learn.microsoft.com/en-us/windows-server/get-started/kms-client-activation-keys)
```cmd
slmgr /ipk WX4NM-KYWYW-QJJR4-XV3QB-6VM33
```
Add your KMS server information to server
```powershell
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform" -Name "KeyManagementServiceName" -Value "KMS_IP"
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform" -Name "KeyManagementServicePort" -Value "KMS_PORT"
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\OfficeSoftwareProtectionPlatform" -Name "KeyManagementServiceName" -Value "KMS_IP"
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\OfficeSoftwareProtectionPlatform" -Name "KeyManagementServicePort" -Value "KMS_PORT"
```
Activate server
```cmd
slmgr /ato
```
*Do not expos your KMS server to the web via port 1688. Microsoft is active scanning the entire internet for public available KMS servers and will issue a take down notice to your ISP!*

## Parent Image
* [python:3.7.10-alpine](https://hub.docker.com/layers/library/python/3.7.10-alpine/images/sha256-932f7a8769b07d1effc5a46cb1463948542a017e82350c93f56792bec08ff9dd?context=explore)

## Built with and thanks to
* [py-kms](https://github.com/Py-KMS-Organization/py-kms)
* [Alpine Linux](https://alpinelinux.org/)

## Tips
* Only use rootless container runtime (podman, rootless docker)
* Don't bind to ports < 1024 (requires root), use NAT/reverse proxy (haproxy, traefik, nginx)
* [Microsoft LICD](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/6c085406-a698-4e12-9d4d-c3b0ee3dbc4a)