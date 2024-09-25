# VRChat VR Phone python controller
Control Microsip using a VRC avatar!

* Install Microsip for the local user
* Setup Microsip settings for your Sip Account
* Install Virtual Audio Cable and setup accordingly (VRChat Output > Microsip Input and vice versa)
* Get a copy of sendosc for windows. [https://github.com/yoggy/sendosc/releases/download/v1.0.2/sendosc-win-1.0.2.zip]

* Edit Microsip.ini in your Appdata folder while Microsip is not running


        cmdOutgoingCall="C:\Users\vrphone\Desktop\VRC VR Phone\sendosc.exe" 127.0.0.1 9001 /microsip/command/cmdOutgoingCall s
        cmdIncomingCall="C:\Users\vrphone\Desktop\VRC VR Phone\sendosc.exe" 127.0.0.1 9001 /microsip/command/cmdIncomingCall s
        cmdCallRing="C:\Users\vrphone\Desktop\VRC VR Phone\sendosc.exe" 127.0.0.1 9001 /microsip/command/cmdCallRing s
        cmdCallAnswer="C:\Users\vrphone\Desktop\VRC VR Phone\sendosc.exe" 127.0.0.1 9001 /microsip/command/cmdCallAnswer s
        cmdCallBusy="C:\Users\vrphone\Desktop\VRC VR Phone\sendosc.exe" 127.0.0.1 9001 /microsip/command/cmdCallBusy s
        cmdCallStart="C:\Users\vrphone\Desktop\VRC VR Phone\sendosc.exe" 127.0.0.1 9001 /microsip/command/cmdCallStart s
        cmdCallEnd="C:\Users\vrphone\Desktop\VRC VR Phone\sendosc.exe" 127.0.0.1 9001 /microsip/command/cmdCallEnd s

* Start Microsip again
* Start VRPhone App
* Clone a public VR Phone VRC avatar or upload your own!

# Disclaimer

This application is not affiliated with VRChat. By using this software you agree to not sue or get upsetti spaghetti with me if it breaks something. Use at your own risk.
Loosely based on code of vrc-owo-suit by Shadoki.


