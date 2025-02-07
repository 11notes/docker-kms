![Banner](https://github.com/11notes/defaults/blob/main/static/img/banner.png?raw=true)

# 🏔️ kms on Alpine
[<img src="https://img.shields.io/badge/github-source-blue?logo=github&color=040308">](https://github.com/11notes/docker-kms)![size](https://img.shields.io/docker/image-size/11notes/kms/646f476?color=0eb305)![version](https://img.shields.io/docker/v/11notes/kms/646f476?color=eb7a09)![pulls](https://img.shields.io/docker/pulls/11notes/kms?color=2b75d6)[<img src="https://img.shields.io/github/issues/11notes/docker-kms?color=7842f5">](https://github.com/11notes/docker-kms/issues)

**Activate any version of Windows and Office, forever**

![activation](https://github.com/11notes/docker-kms/blob/master/img/activation.png "Windows Server 2025 Datacenter")
![GUI](https://github.com/11notes/docker-kms/blob/master/img/GUI.png "11notes/kms-gui")

# SYNOPSIS 📖
**What can I do with this?** This image will run a KMS server you can use to activate any version of Windows and Office, forever. If you need a GUI, simply add [11notes/kms-gui](https://github.com/11notes/docker-kms-gui) to your compose.

Works with:
- Windows Vista 
- Windows 7 
- Windows 8
- Windows 8.1
- Windows 10
- Windows 11
- Windows Server 2008
- Windows Server 2008 R2
- Windows Server 2012
- Windows Server 2012 R2
- Windows Server 2016
- Windows Server 2019
- Windows Server 2022
- Windows Server 2025
- Microsoft Office 2010 ( Volume License )
- Microsoft Office 2013 ( Volume License )
- Microsoft Office 2016 ( Volume License )
- Microsoft Office 2019 ( Volume License )
- Microsoft Office 2021 ( Volume License )
- Microsoft Office 2024 ( Volume License )

# VOLUMES 📁
* **/kms/var** - Directory of the activation database

# COMPOSE ✂️
```yaml
name: "kms"
services:
  kms:
    image: "11notes/kms:646f476"
    container_name: "kms"
    environment:
      TZ: "Europe/Zurich"
    volumes:
      - "var:/kms/var"
    ports:
      - "1688:1688/tcp"
    restart: "always"
  kms-gui:
    image: "11notes/kms-gui:latest"
    container_name: "kms-gui"
    environment:
      TZ: "Europe/Zurich"
    volumes:
      - "var:/kms/var"
    ports:
      - "8080:8080/tcp"
    restart: "always"
volumes:
  var:
```


## Windows Server 2025 Datacenter. List of [GVLK](https://learn.microsoft.com/en-us/windows-server/get-started/kms-client-activation-keys)
```cmd
slmgr /ipk D764K-2NDRG-47T6Q-P8T8W-YP6DF
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

# DEFAULT SETTINGS 🗃️
| Parameter | Value | Description |
| --- | --- | --- |
| `user` | docker | user name |
| `uid` | 1000 | [user identifier](https://en.wikipedia.org/wiki/User_identifier) |
| `gid` | 1000 | [group identifier](https://en.wikipedia.org/wiki/Group_identifier) |
| `home` | /kms | home directory of user docker |
| `database` | /kms/var/kms.db | SQlite database holding all client data |

# ENVIRONMENT 📝
| Parameter | Value | Default |
| --- | --- | --- |
| `TZ` | [Time Zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) | |
| `DEBUG` | Will activate debug option for container image and app (if available) | |
| `KMS_IP` | localhost or 127.0.0.1 or a dedicated IP | 0.0.0.0 |
| `KMS_PORT` | any port > 1024 | 1688 |
| `KMS_LOCALE` | see Microsoft LICD specification | 1033 (en-US) |
| `KMS_ENHANCED_PRIVACY_ID` | set custom ePID (will overwrite KMS_LOCALE) |  |
| `KMS_CLIENTCOUNT` | client count > 25 | 26 |
| `KMS_ACTIVATIONINTERVAL` | Retry unsuccessful after N minutes | 120 (2 hours) |
| `KMS_RENEWALINTERVAL` | re-activation after N minutes | 259200 (180 days) |
| `KMS_LOGLEVEL` | CRITICAL, ERROR, WARNING, INFO, DEBUG, MININFO | INFO |

# SOURCE 💾
* [11notes/kms](https://github.com/11notes/docker-kms)

# PARENT IMAGE 🏛️
* [11notes/alpine:stable](https://hub.docker.com/r/11notes/alpine)

# BUILT WITH 🧰
* [py-kms](https://github.com/Py-KMS-Organization/py-kms)
* [alpine](https://alpinelinux.org)

# GENERAL TIPS 📌
* Use a reverse proxy like Traefik, Nginx, HAproxy to terminate TLS and to protect your endpoints
* Use Let’s Encrypt DNS-01 challenge to obtain valid SSL certificates for your services
* Do not expose this image to WAN! You will get notified from Microsoft via your ISP to terminate the service if you do so
* [Microsoft LICD](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/6c085406-a698-4e12-9d4d-c3b0ee3dbc4a)
  
# ElevenNotes™️
This image is provided to you at your own risk. Always make backups before updating an image to a different version. Check the [releases](https://github.com/11notes/docker-kms/releases) for breaking changes. If you have any problems with using this image simply raise an [issue](https://github.com/11notes/docker-kms/issues), thanks. You can find all my repositories on [github](https://github.com/11notes?tab=repositories).