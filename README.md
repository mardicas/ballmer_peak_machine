# ballmer_peak_machine
DIY can(beer!) dispensing fridge with raspberry pi. This is my first RPI project. We use this machine in our office to dispense beer. Since we all have RFID door cards, then we use the same cards for dispensing beer from a fridge.

## Video
Short demo https://youtu.be/Kdcffz6T2Zw
Look on the inside https://www.youtube.com/watch?v=aPZth4esOSE

## Hardware and OS
 * I am using Raspberry Pi 3 Model B+, but it should work on others too(let me know!)
 * For OS I use https://blog.hypriot.com/getting-started-with-docker-on-your-arm-device/ since it has docker already installed.
 * Make sure spi_bcm2835 module is loaded. (https://pimylifeup.com/raspberry-pi-rfid-rc522/ Setting up Raspbian for the RFID RC522)
 * Disable dtparam=spi=on from /boot/config.txt (https://pimylifeup.com/raspberry-pi-rfid-rc522/ Setting up Raspbian for the RFID RC522)
 
## Schematics
You might need to put resistors on LED ground, but it depends on your LED-s. Concider 330Ω.
![alt text](https://github.com/mardicas/ballmer_peak_machine/blob/master/wiring_bb.png)
![alt text](https://github.com/mardicas/ballmer_peak_machine/blob/master/wiring_schem.png)

You can open wiring.fzz with http://fritzing.org

## Additional packages
```
apt-get install python-rpi.gpio python-mysqldb
pip install mfrc522 gpiozero
```

## Configuration
* Change password of mysql root and identity user in docker-compose.yaml (MYSQL_ROOT_PASSWORD and MYSQL_PASSWORD). 
* Put "identity" users password into automaat.py (Line 69). 
* Put "identity_ro" password into structure.sql (Line 20) and same password into php/index.php (Line 12).
* Change automaat.py GPIO pin values if you have different wiring.

## To build frontend webpage:
```
docker-compose build
```

## To start phpmyadmin, mysql and frontend
```
docker-compose up -d
```

## systemd service
 * The python code (automaat.py) runs as systemd service and it only depends on the mysql server. If you don't want phpmyadmin or frontend you do not need to start them. You can also install or use another mysql server if you wish.
 * You might need to change the path inside of automaat.service to where automaat.py is located on your setup.
```
cp automaat.service /etc/systemd/system/automaat.service
systemctl enable automaat
systemctl start automaat
```
## Managment
* The credit is added using phpmyadmin (users->credit field). 
* When a new RFID card is scanned, then it gets added to users table, but "name" field has to be filled manually first time and 0 credit is given.

## Operational logic
The machine has two slots for drinks - Red and Blue. 
Red Detect detects if there are any drinks in the red slots.
Blue Detect detects if there are any drinks in the blue slots.
If there are no drinks in the Red slot then the "Left LED" glows red.
If there are no drinks in the Blue slot then the "Right LED" glows red.
If there are no drinks in either, then all LEDs are Red.

The green button is a "feeling lucky" button - a lottery. The "Up" LED will start to blink every 15 minutes and when green button is pressed then you have a 1:100 chance to get a free drink. If you did not win then the LEDs will flash Red, if you won then you can select either Red or Blue drink and the lights will be flashing.

If you scan your RFID card and you have credits, then you can choose weather to take from blue or red slots by pressing the red or blue button(the left and right leds will be blinking green). The credits on your card are taken only after you chose a drink. If you don't choose a drink within a minute then the "order" is cancelled.

If you don't have credit on the RFID card or it is a new card then the lights will flash red and you can not get a drink.

The two sets of servos are needed to make sure only one can is released. The "lock" servo is in front of the first can and the other servo is behind it. The behind servos job is to keep the other cans from dropping down before the lock is closed again. The lock servo is stronger and it can take the imact all the dropping cans cause, the regular servo is only able to keep the cans still.


## Debugging
```
journalctl -u automaat.service
docker ps
docker logs <container>
```

## Web interfaces
On http port (TCP 80) you should see UI with statistics, on https(443 HTTPS) port you should see phpmyadmin.
* PHPMYADMIN - https://RPI IP/phpmyadmin
* UI - http://RPI IP/

## Credits, thank you, useful
* https://xkcd.com/323/ for inspiration.
* For blinking led class(I have modified it, but this was the original I used) https://stackoverflow.com/questions/46956380/python-threading-class-for-gpio-led-blink/51888275#51888275
* For RFID reading https://pimylifeup.com/raspberry-pi-rfid-rc522/
* Security audit and testing help https://github.com/EerikKivistik
* Wiring schemas http://fritzing.org/home/
