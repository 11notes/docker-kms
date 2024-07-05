![Banner](https://github.com/11notes/defaults/blob/main/static/img/banner.png?raw=true)

# 🏔️ Alpine - Key Management Server
![size](https://img.shields.io/docker/image-size/11notes/kms/latest?color=0eb305) ![version](https://img.shields.io/docker/v/11notes/kms/latest?color=eb7a09) ![pulls](https://img.shields.io/docker/pulls/11notes/kms?color=2b75d6) ![stars](https://img.shields.io/docker/stars/11notes/kms?color=e6a50e) [<img src="https://img.shields.io/badge/github-11notes-blue?logo=github">](https://github.com/11notes)

**Activate any version of Windows and Office, forever**

# SYNOPSIS
What can I do with this? This image will run a KMS server you can use to activate any version of Windows and Office.

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

# VOLUMES
* **/kms/var** - Directory of the activation database

# COMPOSE
```yaml
version: "3.8"
services:
  kms:
    image: "11notes/kms:latest"
    container_name: "postgres"
    environment:
      TZ: Europe/Zurich
    volumes:
      - "kms-var:/kms/var"
    networks:
      - kms
    restart: always
  whodb:
    image: "11notes/whodb:latest"
    container_name: "whodb"
    environment:
      TZ: Europe/Zurich
    volumes:
      - "kms-var:/whodb/var"
    ports:
      - "8080:8080/tcp"
    networks:
      - kms
      - frontend
    restart: always
volumes:
  kms-var:
networks:
  kms:
    internal: true
  frontend:
```

# EXAMPLES
## Windows Server 2022 Datacenter. List of [GVLK](https://learn.microsoft.com/en-us/windows-server/get-started/kms-client-activation-keys)
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

# DEFAULT SETTINGS
| Parameter | Value | Description |
| --- | --- | --- |
| `user` | docker | user docker |
| `uid` | 1000 | user id 1000 |
| `gid` | 1000 | group id 1000 |
| `home` | /kms | home directory of user docker |
| `database` | /kms/var/kms.db | SQlite database holding all client data |

# ENVIRONMENT
| Parameter | Value | Default |
| --- | --- | --- |
| `TZ` | [Time Zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) | |
| `DEBUG` | Show debug information | |
| `KMS_IP` | localhost or 127.0.0.1 or a dedicated IP | 0.0.0.0 |
| `KMS_PORT` | any port > 1024 | 1688 |
| `KMS_LOCALE` | see Microsoft LICD specification | 1033 (en-US) |
| `KMS_CLIENTCOUNT` | client count >= 25 | 25 |
| `KMS_ACTIVATIONINTERVAL` | Retry unsuccessful after N minutes | 120 (2 hours) |
| `KMS_RENEWALINTERVAL` | re-activation after N minutes | 259200 (180 days) |
| `KMS_LOGLEVEL` | CRITICAL, ERROR, WARNING, INFO, DEBUG, MININFO | INFO |

# PARENT IMAGE
* [11notes/alpine:stable](https://hub.docker.com/r/11notes/alpine)

# BUILT WITH
* [py-kms](https://github.com/Py-KMS-Organization/py-kms)
* [alpine](https://alpinelinux.org)

# TIPS
* Allow non-root ports < 1024 via `echo "net.ipv4.ip_unprivileged_port_start={n}" > /etc/sysctl.d/ports.conf`
* Use a reverse proxy like Traefik, Nginx to terminate TLS with a valid certificate
* Use Let’s Encrypt certificates to protect your SSL endpoints
* [Microsoft LICD](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/6c085406-a698-4e12-9d4d-c3b0ee3dbc4a)

# ElevenNotes<sup>™️</sup>
This image is provided to you at your own risk. Always make backups before updating an image to a new version. Check the changelog for breaking changes. You can find all my repositories on [github](https://github.com/11notes).
    