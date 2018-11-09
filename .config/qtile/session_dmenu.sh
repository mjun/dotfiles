#!/bin/bash
#
# a simple dmenu session script 
#
###

DMENU='dmenu'
choice=$(echo -e "restart qtile\nlogout\nshutdown\nreboot" | $DMENU "$@")

case "$choice" in
  'restart qtile') qtile-cmd -o cmd -f restart & ;;
  logout) qtile-cmd -o cmd -f shutdown & ;;
  shutdown) shutdown -h now & ;;
  reboot) shutdown -r now & ;;
#  suspend) sudo pm-suspend & ;;
#  hibernate) sudo pm-hibernate & ;;
esac
