# auto-turret
Autonomous, networked, and remote controlled nerf turret using rpi

Steps to run:

1. Run test.py on RPI to start camera server
2. Run send_data.py on desktop to send coords (firewall off and connected to same wifi as pi). Also file must be in the same folder as the templates folder which contains index
3. Run TurretProject.py on Rpi to startup the turret
