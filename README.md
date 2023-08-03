# auto-turret
Autonomous, networked, and remote controlled nerf turret using rpi

Steps to run:

1. Run test.py on RPI to start camera server
2. Run send_data.py on desktop to send coords (firewall off and connected to same wifi as pi). Also file must be in the same folder as the templates folder which contains index.html
3. Run TurretProject.py on Rpi to startup the turret

Notes for changes to be done:
1. Ensure TurretProject.py can be run without the coordinates server (stop the crashes when it doesnt recieve and set default behaviour to autonomous unless there is no connection else remote control)
2. Ensure TurretProject.py does not die when there is no controller detected. Also make it detect a new controller being connected.
3. Change the networking from local network to a universally accessible website (maybe with a password?) add the camera feed to the website. This allows it to be remote controlled from anywhere. Server processes autonomous. Client sends remote control commands.
4. Improve computer vision detection settings.
5. Add drive base and limits?
