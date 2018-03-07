#!/bin/bash
# Installation script for the Azubot project.
# Creates Azubot control service.
ask() {
echo -n "Continue? (Y/N)? "
while read -r -n 1 -s answer; do
  if [[ $answer = [YyNn] ]]; then
    [[ $answer = [Yy] ]] && retval=0
    [[ $answer = [Nn] ]] && retval=1
    break
  fi
done
echo  OK
return $retval
}

echo "Make sure the Azubit git is located at /home/pi/Azubot"
if ask; then
	if [ ! -f /etc/init.d/azubot ]; then
		echo "INSTALLING"
		echo "Creating sounds directory in /home/pi/sounds"
		mkdir /home/pi/sounds
        echo "adding demo sound"
        sudo cp /home/pi/Azubot/demo.mp3 /home/pi/sounds/demo.mp3
		echo "creating service in /etc/init.d/azubot"
		sudo cp azubot /etc/init.d/azubot
		sudo chmod +x /etc/init.d/azubot
		sudo update-rc.d azubot defaults
		echo "Azubot service now starts at boot"
		echo "---------------------------------"
		echo "--------------DONE---------------"
		echo "---------------------------------"
	else
		echo "service already installed"
		echo "CANCELLING"
	fi
else
	echo "CANCELLING"
fi
