# Sample Gunicorn configuration file.

bind = '127.0.0.1:5000'
backlog = 2048

workers = 1
worker_class = 'sync'
worker_connections = 1000
timeout = 6000
keepalive = 2

spew = False
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
proc_name = None