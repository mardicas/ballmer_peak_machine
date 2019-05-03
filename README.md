# ballmer_peak_machine
RFID beer dispensing fridge with raspberry pi.

Configuration:
Change password of mysql root and identity user in docker-compose.yaml (MYSQL_ROOT_PASSWORD and MYSQL_PASSWORD). Put "identity" users password into automaat.py (Line 68). Put "identity_ro" password into structure.sql (Line 20), put same password into php/index.php (Line 12).
Change automaat.py GPIO pin values if you have different wiring.

Demo video will be available soon.

To enable systemd service use:
cp automaat.service /etc/systemd/system/automaat.service
systemctl enable automaat
systemctl start automaat
To view logs
journalctl -u automaat.service


To build frontend webpage:
docker-compose build

To start phpmyadmin, mysql and frontend
docker-compose up -d
