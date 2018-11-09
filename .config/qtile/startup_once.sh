#!/bin/bash 
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
nitrogen --restore; sleep 1; compton -b &
nm-applet &
xfce4-power-manager &
pamac-tray &
clipit &
# blueman-applet &
~/.config/qtile/start_conky.sh &
xautolock -time 10 -locker blurlock &
