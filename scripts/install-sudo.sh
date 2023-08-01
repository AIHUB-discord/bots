sudo mkdir /etc/systemd/system/bots

sudo cp systemctl/* /etc/systemd/system/bots

sudo systemctl daemon-reload

sudo systemctl enable bot1