[Unit]
Description=Oscilloscope Flask Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/ceg1010/server.py
WorkingDirectory=/home/pi/oscilloscope
Restart=always
User=pi

[Install]
WantedBy=multi-user.target