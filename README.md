# ballmer_peak_machine
RFID beer dispensing fridge with raspberry pi. This is my first RPI project. We use this machine in our office to dispense beer. Since we all have RFID door cards, then we use the same cards for dispensing beer from a fridge.
The credit is added using phpmyadmin (users->credit field). When an unknown RFID card is scanned, then it gets added to users table, but "name" field has to be filled manually first time.

## Configuration
 * Change password of mysql root and identity user in docker-compose.yaml (MYSQL_ROOT_PASSWORD and MYSQL_PASSWORD). Put "identity" users password into automaat.py (Line 68). Put "identity_ro" password into structure.sql (Line 20), put same password into php/index.php (Line 12).
 * Change automaat.py GPIO pin values if you have different wiring.

## Hardware and OS
 * I am using Raspberry Pi 3 Model B+ with wifi and bluetooth, but it should work fine on different boards too, please let me know if it works on your PI!
 * For OS I use https://blog.hypriot.com/ since it has docker already installed.

## Additional packages
```apt-get install python-rpi.gpio python-mysqldb
pip install mfrc522 gpiozero
```

## To build frontend webpage:
```docker-compose build
```

## To start phpmyadmin, mysql and frontend
```docker-compose up -d
```

## systemd service
 * The python code (automaat.py) runs as systemd service and it only depends on the mysql server. If you don't want phpmyadmin or frontend you do not need to start them. You can also install or use another mysql server if you wish.
```cp automaat.service /etc/systemd/system/automaat.service
systemctl enable automaat
systemctl start automaat
```
## Debugging
```journalctl -u automaat.service
docker ps
docker logs <container>
```



On http port you should see UI with statistics, on https port you should see phpmyadmin.
PHPMYADMIN - https://<RPI IP>/phpmyadmin
UI - http://<RPI IP>/
