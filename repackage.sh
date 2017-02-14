#!/bin/bash

if [ $# -ne 2 ]; then
  echo "Usage:   $0 <zipname>   <username>"
  echo "example: $0 build-02-05 aguibert"
  exit 1
fi

zip -r $1.zip ./src -x \
      '*/settingslocal.py' \
      '*.pyc' \
      'src/static/uploads/*' \
      '*.DS_Store'

echo "Note: If you're not on the ISU network, don't forget to VPN!"
echo "Transferrring $1.zip to nirwebportal. . ."

scp ./$1.zip $2@nirwebportal.vrac.iastate.edu:/home/nirwebportal/archives

echo "Removing local build zip."
rm $1.zip

ssh $2@nirwebportal.vrac.iastate.edu
