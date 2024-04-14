export CURRENT_MODE=TESTING #Used to override operating mode in `src/configs/server_configs.py`
pkill gunicorn #Stop any current process
sleep 5        #Wait for gunicorn to properly exit
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --certfile=/etc/letsencrypt/live/dormdigest.xvm.mit.edu/fullchain.pem \
    --keyfile=/etc/letsencrypt/live/dormdigest.xvm.mit.edu/privkey.pem \
    --capture-output \
    --log-level debug \
    --error-logfile server_error_log.txt \
    --bind 0.0.0.0:8432 \
    --access-logfile server_log.txt &
echo "Done"