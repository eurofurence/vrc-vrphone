# VRChat VR Phone python controller
Control Microsip using a VRC avatar!

* Install Microsip for the local user
* Setup Microsip settings for your Sip Account
* Install Virtual Audio Cable and setup accordingly (VRChat Output > Microsip Input and vice versa)
* Copy callback.ps1 to an appropriate location

* Edit Microsip.ini in your Appdata folder while Microsip is not running

        cmdOutgoingCall=powershell "& ""C:\Users\lcbro\AppData\Roaming\MicroSIP\callback.ps1""" cmdOutgoingCall
        cmdIncomingCall=powershell "& ""C:\Users\lcbro\AppData\Roaming\MicroSIP\callback.ps1""" cmdIncomingCall
        cmdCallRing=powershell "& ""C:\Users\lcbro\AppData\Roaming\MicroSIP\callback.ps1""" cmdCallRing
        cmdCallAnswer=powershell "& ""C:\Users\lcbro\AppData\Roaming\MicroSIP\callback.ps1""" cmdCallAnswer
        cmdCallBusy=powershell "& ""C:\Users\lcbro\AppData\Roaming\MicroSIP\callback.ps1""" cmdCallBusy
        cmdCallStart=powershell "& ""C:\Users\lcbro\AppData\Roaming\MicroSIP\callback.ps1""" cmdCallStart
        cmdCallEnd=powershell "& ""C:\Users\lcbro\AppData\Roaming\MicroSIP\callback.ps1""" cmdCallEnd

* Alternative using cygwin bash & curl

      cmdOutgoingCall="C:\cygwin64\bin\bash.exe" -c '/bin/curl http://127.0.0.1:19001/"$0"/"$1"' cmdOutgoingCall
      cmdIncomingCall="C:\cygwin64\bin\bash.exe" -c '/bin/curl http://127.0.0.1:19001/"$0"/"$1"' cmdIncomingCall
      cmdCallRing="C:\cygwin64\bin\bash.exe" -c '/bin/curl http://127.0.0.1:19001/"$0"/"$1"' cmdCallRing
      cmdCallAnswer="C:\cygwin64\bin\bash.exe" -c '/bin/curl http://127.0.0.1:19001/"$0"/"$1"' cmdCallAnswer
      cmdCallBusy="C:\cygwin64\bin\bash.exe" -c '/bin/curl http://127.0.0.1:19001/"$0"/"$1"' cmdCallBusy
      cmdCallStart="C:\cygwin64\bin\bash.exe" -c '/bin/curl http://127.0.0.1:19001/"$0"/"$1"' cmdCallStart
      cmdCallEnd="C:\cygwin64\bin\bash.exe" -c '/bin/curl http://127.0.0.1:19001/"$0"/"$1"' cmdCallEnd

* Start Microsip again
* Start VRPhone App
* Clone a public VR Phone VRC avatar or upload your own!

# Disclaimer

This application is not affiliated with VRChat. By using this software you agree to not sue or get upsetti spaghetti with me if it breaks something. Use at your own risk.
Loosely based on code of vrc-owo-suit by Shadoki.


