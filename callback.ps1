#Callback script for Microsip
Param([parameter(Position=0, Mandatory=$true)]$action,
      [parameter(Position=1)]$sipuri = "none",
      [parameter(Position=2)]$server = "http://127.0.0.1:19001"
)

Invoke-WebRequest -URI $server/$action/$sipuri
