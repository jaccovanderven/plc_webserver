<#
LiveLink automatisch starten bij inloggen (Windows Taakplanner).

    powershell -ExecutionPolicy Bypass -File autostart.ps1              # installeren en meteen starten
    powershell -ExecutionPolicy Bypass -File autostart.ps1 -Verwijderen # autostart weghalen en server stoppen

De taak draait onder het eigen account bij inloggen (niet bij opstarten), zodat
de VNC-knop de viewer op het bureaublad kan openen. pythonw = geen consolevenster.
Bij een crash herstart Windows de server (3x, elke minuut).
#>
param([switch]$Verwijderen)

$taak = "LiveLink"
$map  = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Verwijderen) {
    Stop-ScheduledTask -TaskName $taak -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $taak -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Autostart '$taak' verwijderd en server gestopt."
    return
}

$python  = (Get-Command python -ErrorAction Stop).Source
$pythonw = Join-Path (Split-Path $python) "pythonw.exe"

$actie = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$map\webserver.py`"" -WorkingDirectory $map
$trigger = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$instellingen = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $taak -Action $actie -Trigger $trigger -Settings $instellingen `
    -Description "LiveLink PLC-webserver (http://localhost:8080) starten bij inloggen" -Force | Out-Null
Start-ScheduledTask -TaskName $taak
Write-Host "Autostart '$taak' geinstalleerd en gestart: http://localhost:8080"
