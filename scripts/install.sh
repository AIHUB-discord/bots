mkdir /etc/systemd/system/bots

cp systemctl/* /etc/systemd/system/bots

systemctl daemon-reload

systemctl enable bot1