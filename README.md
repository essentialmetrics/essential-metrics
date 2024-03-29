# Essential Security Metrics

This repo is part of a small scale study we are conducting to evaluate the effectiveness of a security metrics application for home and small business users. Security metrics applications and frameworks are targeted at medium and large enterprise organizations, leaving the home and small business users in the dark when it comes to security metrics on their systems. This research will look at deploying a security metrics application on a home network and tracking the metrics gathered on the home systems over time. The research will evaluate the data received back and try to answer whether a home metrics application has potential to improve the security posture of similar home and small business networks. 

## Data management

The study has 2 separate databases, one will house your personal data (essential-metrics.db) and the other will house the study data (study-metrics.db). We are keeping the databases separate to reduce the risk of accidentally collecting any personal data from your system.
### Example Data
Please review this example data, this was gathered from a live system and presents a snapshot of the types of data we are aiming to collect: [EXAMPLE-STUDY-DATA](EXAMPLE-STUDY-DATA.md)

## Study instructions
Instructions will be provided over email on how to consent to participate to this study. Please read all material and ask any questions about the study that you need answered. You should know exactly what this study involves and more importantly you should know the explicit data we are collecting from your system.

## Installation instructions

If you have agreed to take part in the study then please follow these steps to install the application on your system. Please do not install the application until the study start date.

## Prerequisites

The study uses nmap and as such this needs to be installed as a third party tool.
NPCAP a packet capturing library for windows must be installed for nmap to work successfully.
This was the only part of the installation we could not automate as the silent installer requires a license.
If you follow these steps in powershell it will install NPCAP on your system as we need it.

```powershell
mkdir C:\opt\installs
Invoke-WebRequest -Uri "https://npcap.com/dist/npcap-1.79.exe" -OutFile "C:\\opt\\installs\\npcap-1.79.exe"
Set-Location C:\opt\installs
./npcap-1.79.exe
```
This will download the npcap exe into a newly created C:\opt directory.
Alternatively you can manually download the package from here: https://npcap.com/#download
This will also launch the install process and take you to the following screens.

**Agree to install**

![Alt text](assets/install.png)

**Agree to the license:**

![Alt text](assets/install-1.png)

**Set install options and start install:**

![Alt text](assets/install-2.png)

## Installation of Application

The rest of this install is automated and can be installed by following these steps in Administrator mode in powershell.

**Open Powershell as Administrator**

Search for powershell, right click and run as Administrator

![Alt text](assets/install-3.png)

**Install and configure application**

This can be run in sections or you can just copy and paste the entire block into powershell and it should complete the entire application install and configuration. We opted to keep the application installation and source in easily readable format so you could see exactly what actions we are performing on your system.

```powershell
Write-Host "Checking Admin permissions and stopping script if not running as admin"

$currentUser = New-Object Security.Principal.WindowsPrincipal $([Security.Principal.WindowsIdentity]::GetCurrent())
if ($currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Output "PowerShell is running as an Administrator, continuing."
} else {
  Add-Type -AssemblyName System.Windows.Forms
  [Windows.Forms.MessageBox]::Show("Please run PowerShell as an Administrator and try again. (Right click and Run as Administrator)", "Administrator Required", [Windows.Forms.MessageBoxButtons]::OK, [Windows.Forms.MessageBoxIcon]::Warning)
  exit
}

Write-Host "Downloading application with git or web-request"
try {
    $gitVersion = git --version
    Write-Host "Git is installed. Version: $gitVersion"
    $repoUrl = "https://github.com/essentialmetrics/essential-metrics.git"
    $clonePath = "C:\\opt\\essential-metrics"
    git clone $repoUrl $clonePath
    Write-Host "Repository cloned successfully to $clonePath"
} catch {
    Write-Host "Git is not installed or not in PATH. Falling back to Invoke-WebRequest."
    $zipUrl = "https://github.com/essentialmetrics/essential-metrics/zipball/master/"
    $destinationPath = "C:\\opt\\installs\\essential-metrics.zip"
    Invoke-WebRequest -Uri $zipUrl -OutFile $destinationPath
    Write-Host "Repository ZIP downloaded successfully to $destinationPath"
    $extractPath = "C:\\opt\\essential-metrics"
    Expand-Archive -LiteralPath $destinationPath -DestinationPath $extractPath
    cd 'C:\opt\essential-metrics\essential*'
    mv * ../
    cd ../
    del essentialmetrics*
    Write-Host "Repository ZIP extracted to $extractPath"
}

Write-Host "Downloading Nmap, python and SQLite DB"

Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe" -OutFile "C:\\opt\\installs\\python-3.12.1-amd64.exe"
Invoke-WebRequest -Uri "https://nmap.org/dist/nmap-7.94-setup.exe" -OutFile "C:\\opt\\installs\\nmap-7.94-setup.exe"

Write-Host "Installing Nmap and Python"
Set-Location C:\opt\installs
.\python-3.12.1-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
.\nmap-7.94-setup.exe /S

sleep 15

Set-Location C:\opt\essential-metrics
& "C:/Program Files/Python312/python.exe" -m venv virtual-env

.\virtual-env\Scripts\pip install -r .\requirements.txt

# Patch the bug in the public python module
$content = Get-Content .\virtual-env\Lib\site-packages\pyreadline\py3k_compat.py
$content = $content -replace "isinstance\(x, collections.Callable\)", "isinstance(x, collections.abc.Callable)"
Set-Content .\virtual-env\Lib\site-packages\pyreadline\py3k_compat.py -Value $content

# Configure Firewall
Set-NetFirewallProfile -LogMaxSizeKilobytes 10240
Set-NetFirewallProfile -LogBlocked True
Set-NetFirewallProfile -LogAllowed True
Set-NetFirewallProfile -Enabled True


# Configure policy event logs for logon
Auditpol /set /subcategory:"Logon" /success:enable /failure:enable
Auditpol /set /subcategory:"Logoff" /success:enable /failure:disable
AuditPol /get /category:"Logon/Logoff"

# Configure policy event logs for process creation
auditpol /set /subcategory:"Process Creation" /success:enable /failure:disable
auditpol /set /subcategory:"Process Termination" /success:enable /failure:disable
auditpol /get /subcategory:"Process Creation"
auditpol /get /subcategory:"Process Termination"

# Configure the scheduled task to collect hourly metrics
$Action = New-ScheduledTaskAction -Execute 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -Argument '-ExecutionPolicy Bypass -File "C:\opt\essential-metrics\gather_metrics_hourly.ps1"'
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 10000)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
Register-ScheduledTask -TaskName "GatherEssentialMetricsHourly" -Action $Action -Trigger $Trigger -Principal $Principal

# Configure the scheduled task to collect daily metrics
$Action = New-ScheduledTaskAction -Execute 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -Argument '-ExecutionPolicy Bypass -File "C:\opt\essential-metrics\gather_metrics_daily.ps1"'
$Trigger = New-ScheduledTaskTrigger -Daily -At '11:15'
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
$Settings = New-ScheduledTaskSettingsSet
$Settings.StartWhenAvailable = $true
Register-ScheduledTask -TaskName "GatherEssentialMetricsDaily" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings

Write-Host "Installation completed"
```

## Initial run of metrics gathering

After the application has been installed we need to run one initialization script to collect all metrics.
The rest will be automated and managed in the two scheduled tasks we have set above.

**This will take between 5 and 10 minutes**

```powershell
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -ExecutionPolicy Bypass -File "C:\opt\essential-metrics\gather_metrics_all.ps1"
```
This will also generate an alert for an EICAR test file, this is the virus scanning test file 

![Alt text](assets/threat.png)


## Starting and running the web application

We have created 2 ways to start and run the application.
The application can be run in user or admin space however if you did not allow npcap to run as non admin users you will get a warning asking you for permission to access them libraries.

### First method

The first is a batch script, this will run the webapp and also connect you to the default browser on the port that the application starts on: http://127.0.0.1:8050

To use this method just double click on the bat file in C:\opt\essential-metrics:

![Alt text](assets/start_bat.png)

### Second method 

The second method is a lnk file that starts the application.
This second method was added as an alternative as it can be pinned to your taskbar when it is run making it very easy to run again in the future.

After you run the application via the lnk file by double clicking on the Metrics.lnk you can right click and pin this to your taskbar:

![Alt text](assets/lnk_pin.png)

With this you can click on the taskbar at any point to run the application in the future.