sudo rm -rf /etc/systemd/system/discord-bot-*

sudo cp systemctl/*.service /etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl enable discord-bot-*