![Windows Server 2025](https://github.com/11notes/docker-${{ json_name }}/blob/master/img/WindowsSRV2025.png?raw=true)
![Windows 11 LTSC 2024](https://github.com/11notes/docker-${{ json_name }}/blob/master/img/Windows11ENTLTSC.png?raw=true)
![Web GUI](https://github.com/11notes/docker-${{ json_name }}/blob/master/img/webGUICustomIcon.png?raw=true)

${{ content_synopsis }} This image will run a KMS server you can use to activate any version of Windows and Office, forever.

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

${{ title_volumes }}
* **${{ json_root }}/var** - Directory of the activation database

${{ content_compose }}

# EXAMPLE
## Windows Server 2025 Datacenter. List of [GVLK](https://learn.microsoft.com/en-us/windows-server/get-started/kms-client-activation-keys)
```cmd
slmgr /ipk D764K-2NDRG-47T6Q-P8T8W-YP6DF
```
Add your KMS server information to server via registry
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

${{ content_defaults }}
| `database` | /kms/var/kms.db | SQlite database holding all client data |

${{ content_environment }}
| `KMS_LOCALE` | see Microsoft LICD specification | 1033 (en-US) |
| `KMS_CLIENTCOUNT` | client count > 25 | 26 |
| `KMS_ACTIVATIONINTERVAL` | Retry unsuccessful after N minutes | 120 (2 hours) |
| `KMS_RENEWALINTERVAL` | re-activation after N minutes | 259200 (180 days) |
| `KMS_LOGLEVEL` | CRITICAL, ERROR, WARNING, INFO, DEBUG, MININFO | INFO |

${{ content_source }}

${{ content_parent }}

${{ content_built }}

${{ content_tips }}
* Do not expose this image to WAN! You will get notified from Microsoft via your ISP to terminate the service if you do so
* [Microsoft LICD](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/6c085406-a698-4e12-9d4d-c3b0ee3dbc4a)
* Use [11notes/kms-gui](https://github.com/11notes/docker-kms-gui) if you want to see the clients you activated in a nice web GUI