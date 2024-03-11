export CURRENT_MODE=TESTING #Used to override operating mode in `src/configs/server_configs.py`
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --capture-output \
    --log-level debug \
    --error-logfile server_error_log.txt \
    --bind 0.0.0.0:8432 \
    --access-logfile server_log.txt &