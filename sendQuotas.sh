#!/bin/bash

#grep pi_zhao /ycga-gpfs/.mmrepquota/current > /tmp/zhao.txt && echo "RUDDLE zhao PI quota report" | mail -a /tmp/zhao.txt -c robert.bjornson@yale.edu -s "Zhao quota report" dingjue.ji@yale.edu && rm /tmp/zhao.txt
grep pi_zhao /ycga-gpfs/.mmrepquota/current > /tmp/zhao.txt && echo "RUDDLE zhao PI quota report" | mail -a /tmp/zhao.txt -c robert.bjornson@yale.edu -s "Ruddle Zhao quota report" robert.bjornson@yale.edu && rm /tmp/zhao.txt

