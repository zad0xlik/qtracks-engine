#!/bin/bash

set -e

eval $(printenv | awk -F= '{print "export " "\""$1"\"""=""\""$2"\"" }' >> /etc/profile)
echo 'Start main app through gunicorn - app.py'

# kill all screens
#killall SCREEN

# shutdown server redis if running on local
#redis-cli -a otsosika shutdown

#screen -dm bash -c "gunicorn --certfile=/qtracks/server/cert.pem --keyfile=/qtracks/server/privkey.pem --bind 0.0.0.0:5000 app:app" & GUNIC=$!
#screen -S app -dm bash -c "gunicorn --certfile=/Users/fkolyadin/Desktop/rnd/model_approaches/development/qtrack/qtracks/server/cert.pem --keyfile=/Users/fkolyadin/Desktop/rnd/model_approaches/development/qtrack/qtracks/server/privkey.pem --bind 0.0.0.0:5000 app:app" & GUNIC=$!
gunicorn --certfile=server/cert.pem --keyfile=server/privkey.pem --bind 0.0.0.0:5000 app:app & GUNIC=$!
status=$?
if [ $status -ne 0 ]; then
    echo "Failed to start cron process: $status"
  exit $status
fi

screen -S redis-server -dm bash -c "redis-server modules/Db/redis.conf" & REDIS=$!
status=$?
if [ $status -ne 0 ]; then
    echo "Failed to start cron process: $status"
  exit $status
fi

wait $GUNIC
wait $REDIS

screen -S streamorders -dm bash -c "python3.7 qtracks.py streamorders" & STRORD=$!
status=$?

if [ $status -ne 0 ]; then
    echo "Failed to start cron process: $status"
  exit $status
fi

wait $STRORD

screen -S pricing -dm bash -c "python3.7 qtracks.py pricing" & PRICIN=$!
status=$?

if [ $status -ne 0 ]; then
    echo "Failed to start cron process: $status"
  exit $status
fi

screen -S streamchain -dm bash -c "python3.7 qtracks.py streamchain" & STRCHN=$!
status=$?

if [ $status -ne 0 ]; then
    echo "Failed to start cron process: $status"
  exit $status
fi

screen -S sendorders -dm bash -c "python3.7 qtracks.py sendorders" & SNDORD=$!
status=$?

if [ $status -ne 0 ]; then
    echo "Failed to start cron process: $status"
  exit $status
fi

wait $PRICIN
wait $STRCHN
wait $SNDORD

#echo 'Starting cron'
#cron -f & CRONEX=$!
#status=$?
#if [ $status -ne 0 ]; then
#    echo "Failed to start cron process: $status"
#  exit $status
#fi
#
## Start the first streamlit process
#streamlit run streamlit/main.py & STRMLT=$!
#status=$?
#if [ $status -ne 0 ]; then
#  echo "Failed to start streamlit process: $status"
#  exit $status
#fi
#
#
## Start the second jupyter-lab process
#jupyter lab --ip='0.0.0.0' --port=8888 --no-browser --allow-root & JPTRLB=$!
#status=$?
#if [ $status -ne 0 ]; then
#  echo "Failed to start jupyter lab process: $status"
#  exit $status
#fi
#
#wait $STRMLT
#wait $JPTRLB
#wait $CRONEX