#prometheus node exporter installation

1. **create directory**:
```cmd
mkdir /opt/node_exporter
cd /opt/node_exporter
```
2. **download file**:
```cmd
wget https://github.com/prometheus/node_exporter/releases/download/v1.8.2/node_exporter-1.8.2.linux-amd64.tar.gz
```
3. **unzip**:
```cmd
tar xvfz node_exporter-1.8.2.linux-amd64.tar.gz
```
4. **create service**:
```cmd
nano /etc/systemd/system/node_exporter.service

[Unit]
Description=Node Exporter

[Service]
User=root
Group=root
#EnvironmentFile=-/etc/sysconfig/node_exporter
ExecStart=/opt/node_exporter/node_exporter-1.3.1.linux-amd64/node_exporter

[Install]
WantedBy=multi-user.target
```
5. **enable service**:
```cmd
systemctl daemon-reload
systemctl enable node_exporter
systemctl start node_exporter
systemctl status node_exporter
```
