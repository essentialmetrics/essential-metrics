# Essential Security Metrics Uninstall Instructions

These instructions are for removing all aspects of the study application after the study has completed.<br>
**Please only run these when instructed.**

### Remove scheduled tasks, study data and application
**Open Powershell as Administrator**

Search for powershell, right click and run as Administrator

![Alt text](assets/install-3.png)

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

Unregister-ScheduledTask -TaskName "GatherEssentialMetricsDaily" -Confirm:$false
Unregister-ScheduledTask -TaskName "GatherEssentialMetricsHourly" -Confirm:$false

del C:\opt\essential-metrics

Write-Host "Uninstall completed"
```
## Uninstall pre-requisite programs

Open control panel and locate Programs and Features.<br>
Click on each of these programs one by one and click uninstall:

![alt text](assets/uninstall.png)

Thanks again for your help with the study!