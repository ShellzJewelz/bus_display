# Bus Information Display

This project displays the bus arrival times that you configured at the given bus stops that you chose.
The project runs on a Raspberry Pi and only works with Israel's buses. This is not an international solution.

## Installation

Follow the steps below to install the project:

1. Clone the repository
```bash
git clone https://github.com/ShellzJewelz/bus_display.git
```
2. Navigate into the directory
```bash
cd bus_display
```
3. Copy the project files to the location the service expects
```bash
sudo cp ./bus_display /bin/
```
4. Copy or create a configuration file using the provided example .yaml file
```bash
sudo mkdir /etc/bus_display
sudo cp ./busfilter.yaml /etc/bus/display/
```
5. Copy service unit file
```bash
cp bus-display.service ~/.config.systemd/user/
```
6. Enable the user service
```bash
systemctl --user enable bus-display.service
```
7. Copy autostart desktop entry file
```bash
cp fullscreen-firefox.desktop ~/.config/autostart/
```
