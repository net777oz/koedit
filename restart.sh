pkill -f "python3.*/app.py" || true
sleep 1
source venv/bin/activate
nohup python3 app.py > flask.log 2>&1 &
