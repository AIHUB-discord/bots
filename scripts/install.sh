rm -rf /etc/systemd/system/discord-bot-*

cp systemctl/*.service /etc/systemd/system/

systemctl daemon-reload

systemctl enable discord-bot-*