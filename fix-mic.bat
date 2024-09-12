echo off
SoundVolumeView.exe /Disable "CABLE-B Input"
REM timeout /t 1 /nobreak > nul
SoundVolumeView.exe /Enable "CABLE-B Input"
