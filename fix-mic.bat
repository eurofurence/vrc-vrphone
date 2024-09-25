echo off
:start
echo Resetting Sound Device
SoundVolumeView.exe /Disable "CABLE-B Input"
SoundVolumeView.exe /Enable "CABLE-B Input"
echo Done! Waiting for 1 hour for next reset. Consider restarting the VRC client every 24 hours
timeout /t 3600 /nobreak > nul
goto start
