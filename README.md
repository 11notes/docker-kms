![banner](https://raw.githubusercontent.com/11notes/static/refs/heads/master/img/banner/README.png)

# KMS
![size](https://img.shields.io/badge/image_size-102MB-green?color=%2338ad2d)![5px](https://raw.githubusercontent.com/11notes/static/refs/heads/master/img/markdown/transparent5x2px.png)![pulls](https://img.shields.io/docker/pulls/11notes/kms?color=2b75d6)![5px](https://raw.githubusercontent.com/11notes/static/refs/heads/master/img/markdown/transparent5x2px.png)[<img src="https://img.shields.io/github/issues/11notes/docker-kms?color=7842f5">](https://github.com/11notes/docker-kms/issues)![5px](https://raw.githubusercontent.com/11notes/static/refs/heads/master/img/markdown/transparent5x2px.png)![swiss_made](https://img.shields.io/badge/Swiss_Made-FFFFFF?labelColor=FF0000&logo=data:image/svg%2bxml;base64,PHN2ZyB2ZXJzaW9uPSIxIiB3aWR0aD0iNTEyIiBoZWlnaHQ9IjUxMiIgdmlld0JveD0iMCAwIDMyIDMyIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgogIDxyZWN0IHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgZmlsbD0idHJhbnNwYXJlbnQiLz4KICA8cGF0aCBkPSJtMTMgNmg2djdoN3Y2aC03djdoLTZ2LTdoLTd2LTZoN3oiIGZpbGw9IiNmZmYiLz4KPC9zdmc+)

Activate any version of Windows and Office, forever

![Windows Server 2025](https://github.com/11notes/docker-kms/blob/master/img/WindowsSRV2025.png?raw=true)

![Web GUI](https://github.com/11notes/docker-kms/blob/master/img/webGUICustomIcon.png?raw=true)

# SYNOPSIS 📖
**What can I do with this?** This image will run a KMS server you can use to activate any version of Windows and Office, forever.

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

x-lockdown: &lockdown
  # prevents write access to the image itself
  read_only: true
  # prevents any process within the container to gain more privileges
  security_opt:
    - "no-new-privileges=true"

services:
  server:
    image: "11notes/kms:1.0.3"
    <<: *lockdown
    environment:
      TZ: "Europe/Zurich"
    volumes:
      - "server.var:/kms/var"
    networks:
      frontend:
    ports:
      - "1688:1688/tcp"
    restart: "always"

  gui:
    depends_on:
      server:
        condition: "service_healthy"
        restart: true
    image: "11notes/kms-gui:1.0.3"
    environment:
      TZ: "Europe/Zurich"
    volumes:
      - "server.var:/kms/var"
    networks:
      frontend:
    ports:
      - "3000:3000/tcp"
    restart: "always"

volumes:
  server.var:

networks:
  frontend:
```
To find out how you can change the default UID/GID of this container image, consult the [RTFM](https://github.com/11notes/RTFM/blob/main/linux/container/image/11notes/how-to.changeUIDGID.md#change-uidgid-the-correct-way).

# EXAMPLE
## Add your product key
Windows Server 2025 Datacenter. List of [GVLK](https://learn.microsoft.com/en-us/windows-server/get-started/kms-client-activation-keys)
```cmd
slmgr /ipk D764K-2NDRG-47T6Q-P8T8W-YP6DF
```
## Add your KMS server information
... via CLI
```
 slmgr /skms KMS_IP:KMS_PORT
```
... via registry (or add these key to your GPO)
```powershell
"Windows"
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform" -Name "KeyManagementServiceName" -Value "KMS_IP"
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform" -Name "KeyManagementServicePort" -Value "KMS_PORT"

"Office"
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\OfficeSoftwareProtectionPlatform" -Name "KeyManagementServiceName" -Value "KMS_IP"
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\OfficeSoftwareProtectionPlatform" -Name "KeyManagementServicePort" -Value "KMS_PORT"
```
... via DNS
```sh
# BIND
_vlmcs._tcp SRV 0 0 KMS_PORT KMS_IP
```
## Activate server
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
| `KMS_LOCALE` | see Microsoft LICD specification | 1033 (en-US) |
| `KMS_ACTIVATIONINTERVAL` | Retry unsuccessful after N minutes | 120 (2 hours) |
| `KMS_RENEWALINTERVAL` | re-activation after N minutes | 259200 (180 days) |

# MAIN TAGS 🏷️
These are the main tags for the image. There is also a tag for each commit and its shorthand sha256 value.

* [1.0.3](https://hub.docker.com/r/11notes/kms/tags?name=1.0.3)

### There is no latest tag, what am I supposed to do about updates?
It is my opinion that the ```:latest``` tag is a bad habbit and should not be used at all. Many developers introduce **breaking changes** in new releases. This would messed up everything for people who use ```:latest```. If you don’t want to change the tag to the latest [semver](https://semver.org/), simply use the short versions of [semver](https://semver.org/). Instead of using ```:1.0.3``` you can use ```:1``` or ```:1.0```. Since on each new version these tags are updated to the latest version of the software, using them is identical to using ```:latest``` but at least fixed to a major or minor version. Which in theory should not introduce breaking changes.

If you still insist on having the bleeding edge release of this app, simply use the ```:rolling``` tag, but be warned! You will get the latest version of the app instantly, regardless of breaking changes or security issues or what so ever. You do this at your own risk!

# REGISTRIES ☁️
```
docker pull 11notes/kms:1.0.3
docker pull ghcr.io/11notes/kms:1.0.3
docker pull quay.io/11notes/kms:1.0.3
```

# SOURCE 💾
* [11notes/kms](https://github.com/11notes/docker-kms)

# PARENT IMAGE 🏛️
* [11notes/python:3.15](https://hub.docker.com/r/11notes/python)

# BUILT WITH 🧰
* [11notes/py-kms](https://github.com/11notes/fork-py-kms)
* [11notes/util](https://github.com/11notes/docker-util)

# GENERAL TIPS 📌
> [!TIP]
>* Use a reverse proxy like Traefik, Nginx, HAproxy to terminate TLS and to protect your endpoints
>* Use Let’s Encrypt DNS-01 challenge to obtain valid SSL certificates for your services
* Do not expose this image to WAN! You will get notified from Microsoft via your ISP to terminate the service if you do so
* [Microsoft LICD](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/6c085406-a698-4e12-9d4d-c3b0ee3dbc4a)
* Use [11notes/kms-gui](https://github.com/11notes/docker-kms-gui) if you want to see the clients you activated in a nice web GUI

# ElevenNotes™️
This image is provided to you at your own risk. Always make backups before updating an image to a different version. Check the [releases](https://github.com/11notes/docker-kms/releases) for breaking changes. If you have any problems with using this image simply raise an [issue](https://github.com/11notes/docker-kms/issues), thanks. If you have a question or inputs please create a new [discussion](https://github.com/11notes/docker-kms/discussions) instead of an issue. You can find all my other repositories on [github](https://github.com/11notes?tab=repositories).

*created 19.10.2026, 15:12:16 (CET)*