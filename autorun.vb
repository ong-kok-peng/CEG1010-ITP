[Unit]
Description=Oscilloscope Flask Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/ceg1010/server.py
WorkingDirectory=/home/ceg1010
Restart=always
User=ceg1010

[Install]
WantedBy=multi-user.target