#!/bin/bash

grep pi_gerstein /ysm-gpfs/.mmrepquota/current > /tmp/gerstein.txt && echo "gerstein PI quota report" | mail -a /tmp/gerstein.txt -c robert.bjornson@yale.edu -s "gerstein PI quota report" gamze.gursoy@yale.edu && rm /tmp/gerstein.txt

grep pi_zhao /ysm-gpfs/.mmrepquota/current > /tmp/zhao.txt && echo "zhao PI quota report" | mail -a /tmp/zhao.txt -c robert.bjornson@yale.edu -s "Zhao quota report" dingjue.ji@yale.edu && rm /tmp/zhao.txt

