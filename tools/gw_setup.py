import sys
import telnetlib

HOST = '192.168.10.1'

user = "admin"

password = "admin"

tn = telnetlib.Telnet(HOST, 23, 1)
tn.set_debuglevel(100)


tn.read_until("login:")
tn.write(user + "\n")


tn.read_until("password:")
tn.write(password + "\n")


# tn.write("WIFI MODE 1\n")
# tn.write("WIFI STASSID Save-On-Foods\n")


commands = ['WIFI MODE 1', 'WIFI STASSID Save-On-Foods', 'WIFI STASECT OPEN', 'WIFI STASECK', 
'SYS WORKMODE 2', 'HTTP HOST 52.91.226.215', 'HTTP PORT 80', 'HTTP URLPATH /intake', 'SYS REQINTVL 15', 
'HTTP KEEPALIVE 1', 'SYS GPRPWL 0000000000000000002F23 000000000000000000FFFF', 'NTP ENABLE 1',
'NTP SERVER pool.ntp.org', 'NTP SYNCINTVL 600', 'REBOOT 0']

for command in commands:
	tn.write(command + "\n")

