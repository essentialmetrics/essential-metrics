# Essential Security Metrics Update Instructions

These update instructions were created incase any bug is identified in the code and an update needs to be implemented on your system.
If you have been asked to update the application please run these instruction steps below.


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

Write-Host "Downloading application with git or web-request"
try {
    $gitVersion = git --version
    Write-Host "Git is installed. Version: $gitVersion"
    Set-Location C:\opt\essential-metrics
    git pull
    if (-not $?) {
        throw "Git pull failed due to local changes that would be overwritten."
    }
} catch {
    Write-Host "Git is not installed, not in PATH, or git pull failed. Falling back to Invoke-WebRequest."
    $zipUrl = "https://github.com/essentialmetrics/essential-metrics/zipball/master/"
    $destinationPath = "C:\\opt\\installs\\essential-metrics.zip"
    Invoke-WebRequest -Uri $zipUrl -OutFile $destinationPath
    Write-Host "Repository ZIP downloaded successfully to $destinationPath"
    $extractPath = "C:\\opt\\essential-metrics-update"
    Expand-Archive -LiteralPath $destinationPath -DestinationPath $extractPath
    Copy-Item -Path "C:\opt\essential-metrics-update\essentialmetrics*\*" -Destination "C:\opt\essential-metrics" -Recurse -Force

    Remove-Item -Path "C:\\opt\\installs\\essential-metrics.zip"
    Remove-Item -Path "C:\\opt\\essential-metrics-update" -Recurse
    Write-Host "Repository ZIP extracted to $extractPath"
}

Write-Host "Update completed"
```
