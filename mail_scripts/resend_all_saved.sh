#!/bin/bash

saved_folder="./saved"

for file in "$saved_folder"/*; do
   if [ -f "$file" ]; then
      filename=$(basename "$file")
      # make sure the filename doesn't start with "." or "_"
      # and make sure it ends with ".txt" or ".eml"
      if [[ ! "$filename" =~ ^[._] && ( "$filename" =~ \.txt$ || "$filename" =~ \.eml$ ) ]]; then
         echo "Resending \`$file\`..."
         /usr/bin/python3 send_to_backend.py < "$file"
      fi
   fi
done




