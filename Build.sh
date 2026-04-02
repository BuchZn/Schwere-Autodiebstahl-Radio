#!/bin/bash

# Prüfen, ob das Script als Root ausgeführt wird
if [ "$EUID" -ne 0 ]; then
  echo "Please use start the Script with sudo $0"
  exit
fi

echo "--- Start the GTA-PI Setup ---"
echo "               ┳┓    ┳┓   ┓ ┏┓    "
echo "               ┣┫┓┏  ┣┫┓┏┏┣┓┏┛┏┓  "
echo "               ┻┛┗┫  ┻┛┗┻┗┛┗┗┛┛┗  "
echo "                  ┛              "

echo "------------------------------------------------------------"
echo "[1/12] Create Backup of current Mirrors..."
echo "------------------------------------------------------------"
cp /etc/apt/sources.list /etc/apt/sources.list.bak
cp /etc/apt/sources.list.d/raspi.list /etc/apt/sources.list.d/raspi.list.bak


echo "------------------------------------------------------------"
echo "[2/12] Update /etc/apt/sources.list (Legacy Mirror)..."
echo "------------------------------------------------------------"
cat <<EOF > /etc/apt/sources.list
deb http://legacy.raspbian.org/raspbian/ buster main contrib non-free rpi
# deb-src http://legacy.raspbian.org/raspbian/ buster main contrib non-free rpi
EOF


echo "------------------------------------------------------------"
echo "[3/12] Update /etc/apt/sources.list.d/raspi.list..."
echo "------------------------------------------------------------"
cat <<EOF > /etc/apt/sources.list.d/raspi.list
deb http://archive.raspberrypi.org/debian/ buster main
EOF


echo "------------------------------------------------------------"
echo "[4/12] Run apt-get update (Force IPv4 & ReleaseInfo Change)..."
echo "NOTE: Do NOT run ‘apt upgrade’ afterward to protect flexfb!"
echo "------------------------------------------------------------"

apt-get update -o Acquire::ForceIPv4=true --allow-releaseinfo-change

echo "------------------------------------------------------------"
echo "Finished Mirrow update if no 404 was found."
echo "[5/12] Configure kernel modules..."
echo "------------------------------------------------------------"


for mod in spi-bcm2835 flexfb fbtft_device; do
    if ! grep -q "$mod" /etc/modules; then
        echo "$mod" >> /etc/modules
        echo "Modul $mod hinzugefügt."
    fi
done

echo "------------------------------------------------------------"
echo "[6/12] Create /etc/modprobe.d/fbtft.conf..."
echo "------------------------------------------------------------"
cat <<EOF > /etc/modprobe.d/fbtft.conf
options fbtft_device name=flexfb gpios=reset:27,dc:25,cs:8,led:18 speed=40000000 bgr=1 fps=60 custom=1 height=240 width=240
options flexfb setaddrwin=0 width=240 height=240 init=-1,0x11,-2,120,-1,0xEF,-1,0xEB,0x14,-1,0xFE,-1,0xEF,-1,0xEB,0x14,-1,0x84,0x40,-1,0x85,0xFF,-1,0x86,0xFF,-1,0x87,0xFF,-1,0x88,0x0A,-1,0x89,0x21,-1,0x8A,0x00,-1,0x8B,0x80,-1,0x8C,0x01,-1,0x8D,0x01,-1,0x8E,0xFF,-1,0x8F,0xFF,-1,0xB6,0x00,0x20,-1,0x36,0x08,-1,0x3A,0x05,-1,0x90,0x08,0x08,0x08,0x08,-1,0xBD,0x06,-1,0xBC,0x00,-1,0xFF,0x60,0x01,0x04,-1,0xC3,0x13,-1,0xC4,0x13,-1,0xC9,0x22,-1,0xBE,0x11,-1,0xE1,0x10,0x0E,-1,0xDF,0x21,0x0c,0x02,-1,0xF0,0x45,0x09,0x08,0x08,0x26,0x2A,-1,0xF1,0x43,0x70,0x72,0x36,0x37,0x6F,-1,0xF2,0x45,0x09,0x08,0x08,0x26,0x2A,-1,0xF3,0x43,0x70,0x72,0x36,0x37,0x6F,-1,0xED,0x1B,0x0B,-1,0xAE,0x77,-1,0xCD,0x63,-1,0x70,0x07,0x07,0x04,0x0E,0x0F,0x09,0x07,0x08,0x03,-1,0xE8,0x34,-1,0x62,0x18,0x0D,0x71,0xED,0x70,0x70,0x18,0x0F,0x71,0xEF,0x70,0x70,-1,0x63,0x18,0x11,0x71,0xF1,0x70,0x70,0x18,0x13,0x71,0xF3,0x70,0x70,-1,0x64,0x28,0x29,0xF1,0x01,0xF1,0x00,0x07,-1,0x66,0x3C,0x00,0xCD,0x67,0x45,0x45,0x10,0x00,0x00,0x00,-1,0x67,0x00,0x3C,0x00,0x00,0x00,0x01,0x54,0x10,0x32,0x98,-1,0x74,0x10,0x85,0x80,0x00,0x00,0x4E,0x00,-1,0x98,0x3e,0x07,-1,0x35,-1,0x21,-1,0x11,-2,12,-1,0x29,-2,2,-3
EOF

echo "------------------------------------------------------------"
echo "[7/12] Install Build-Tools and compile fbcp..."
echo "------------------------------------------------------------"

apt-get update -o Acquire::ForceIPv4=true --allow-releaseinfo-change
apt-get install -y cmake git

cd /home/pi
if [ ! -d "rpi-fbcp" ]; then
    git clone https://github.com/tasanakorn/rpi-fbcp
fi
cd rpi-fbcp/
mkdir -p build
cd build/
cmake ..
make
install fbcp /usr/local/bin/fbcp

echo "------------------------------------------------------------"
echo "[8/12] Optimize HDMI Configurations in /boot/config.txt..."
echo "------------------------------------------------------------"

if ! grep -q "hdmi_cvt=300 300" /boot/config.txt; then
cat <<EOF >> /boot/config.txt

# Round Display Settings
hdmi_force_hotplug=1
hdmi_cvt=300 300 60 1 0 0 0
hdmi_group=2
hdmi_mode=87
display_rotate=1
EOF
fi

echo "------------------------------------------------------------"
echo "[9/12] Configuring audio for HiFiBerry DAC teeBlacklist onboard sound"
echo "------------------------------------------------------------"

echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/alsa-blacklist.conf

echo "------------------------------------------------------------"
echo "[10/12] Comment out onboard audio and add DAC overlay in config.txt"
echo "------------------------------------------------------------"

sudo sed -i 's/^dtparam=audio=on/#dtparam=audio=on/' /boot/firmware/config.txt
echo "dtoverlay=hifiberry-dac" | sudo tee -a /boot/firmware/config.txt

echo "------------------------------------------------------------"
echo "[11/12] Write ALSA config"
echo "------------------------------------------------------------"

sudo tee /etc/asound.conf > /dev/null <<EOF
pcm.!default {
    type hw
    card 0
}
ctl.!default {
    type hw
    card 0
}
EOF


echo "------------------------------------------------------------"
echo "[12/12] Konfiguration abgeschlossen!"
echo "------------------------------------------------------------"
echo "Do you want to download the GTA-Radio Files ? (y/n)"
read c
if [[ "$c" == "y" || "$confirm" == "yes" ]]; then
    echo "------------------------------------------------------------"
    echo "[1/1] Downloading Repository"
    echo "------------------------------------------------------------"
    cd /home/pi
    git clone https://github.com/BuchZn/Schwere-Autodiebstahl-Radio.git
    cd Schwere-Autodiebstahl-Radio/

    echo "Do you want to activate the Radio System Service? (y/n)"
    read cc
    if [[ "$cc" == "y" || "$confirm" == "yes" ]]; then

        echo "------------------------------------------------------------"
        echo "[1/5] Add Schwere-Autodiebstahl-Radio Service to /etc/systemd/system/"
        echo "------------------------------------------------------------"

        cd /home/pi/Schwere-Autodiebstahl-Radio
        sudo cp ./Schwere-Autodiebstahl-Radio.service /etc/systemd/system/Schwere-Autodiebstahl-Radio.service

        echo "------------------------------------------------------------"
        echo "[2/5] Installing system dependencies..."
        echo "------------------------------------------------------------"

        sudo apt-get install -y \
            python3-pip \
            python3-pil \
            python3-rpi.gpio \
            python3-dev \
            libjpeg-dev \
            zlib1g-dev

        echo "------------------------------------------------------------"
        echo "[3/4] Installing Python packages..."
        echo "------------------------------------------------------------"
        pip3 install --break-system-packages \
            Pillow \
            RPi.GPIO


        echo "------------------------------------------------------------"
        echo "[4/5] Reloading System Daemon "
        echo "------------------------------------------------------------"
        sudo systemctl daemon-reload
        echo "------------------------------------------------------------"
        echo "[5/5] Enable  Schwerer-Autodiebstahl-Service "
        echo "------------------------------------------------------------"

        sudo systemctl enable Schwere-Autodiebstahl-Radio
    fi



fi



echo "There is a Pending update the system needs to Reboot"
echo "After the Reboot fbcp should be ready."
echo "If you installed the Radio Service remove the SD-After the reboot and Move your own MP3 and JPEG Files in the Designated Folders."
echo "Run the bin_Creater.py to create bin Files of every Image to make the Service Start faster"
echo "Should the System reboot now? (y/n)"
read confirm
if [[ "$confirm" == "y" ||  "$confirm" == "yes" ]]; then
    reboot
fi
