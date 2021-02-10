whereto="127.0.0.1:5000/execute"
for i in `seq 1 300`; do (curl http://${whereto}?cmd="ls"&options="-lRrth"&path="." &) ; done
