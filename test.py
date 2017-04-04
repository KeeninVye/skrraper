from subprocess import Popen, PIPE

p1 = Popen(['python', 'auth_server.py'], stdout=PIPE)
p2 = Popen(['open', 'http://localhost:8888/callback/'])
print(p1.communicate())
p2.kill()