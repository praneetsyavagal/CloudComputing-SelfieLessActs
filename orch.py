import docker
import threading
from flask import Flask, render_template, request, redirect
from flask import Flask
from datetime import datetime
import requests
import threading
client=docker.from_env()
next_port=8000
curr_port = 0
ACTS_IP="http://localhost"
#'54.162.187.144'
req=0
reqcnt=0
active_ports = [8000]
app = Flask(__name__)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods = ['GET','POST', 'DELETE'])
def catch_all(path):
	cd=client.containers.list()
	#print((cd[0].__dict__)['attrs']['NetworkSettings']['Ports']['80/tcp'][0]['HostPort'],'444444444444444444444444444')
	print(cd)
	global req
	global reqcnt
	global curr_port
	global active_ports
	global ACTS_IP
	if path == "":
		return "",200
	req+=1
	reqcnt+=1
	timer3=threading.Timer(120.0, timer4)
	timer3.start()
#	print(request.method,reqcnt)
	cd=client.containers.list()
	url =(ACTS_IP + ":" + str(8000+curr_port) +"/"+ path)
	curr_port = (curr_port + 1)%len(cd)
	print(request.method,reqcnt)
	print('ggg',curr_port)
	#%len(active_ports)
	headers = {'content-type': 'application/json'}
	try:
		if(request.method=='POST'):
			r = requests.post(url,json=request.json,headers=headers)
		elif(request.method == 'GET'):
 			r=requests.get(url,json=requests.json,headers=headers)
		elif(request.method == "DELETE"):
			r=requests.delete(url,json=requests.json,headers=headers)
		else:
			return ''
	except:
		if(request.method == 'GET'):
			r=requests.get(url,headers=headers)
		elif(request.method == "DELETE"):
			r=requests.delete(url,headers=headers)
		else:
			return ''
	return r._content,r.status_code
	return ''
	return redirect(ACTS_IP + ":" + str(active_ports[curr_port-1]) +"/"+ path, code = 307)
def start_monitor():
	timer=threading.Timer(0.0, timer4)
	timer.start()
def timer4():
	#timer2=threading.Timer(120.0, timer4)
	#timer2.start()
	global reqcnt
	print(reqcnt,"sss")
	cd=client.containers.list()
	if (int(reqcnt/20)+1 >(int(len(cd)))):
		new_container()
                reqcnt=0
	else:
		delete_container()
                reqcnt=0
       	timer2=threading.Timer(120.0, timer4)
        timer2.start()
	#timer()
def new_container():
	global reqcnt
	print("new conatiner time")
	cd=client.containers.list()
	try:
		while((reqcnt/20)+1>int(len(cd))):
			next_port=8000+int(len(cd))
			new=80
			client.containers.run('acts',ports={new:next_port},detach=True)
		cd=client.containers.list()
	except: pass
	reqcnt=0
def delete_container():
	global reqcnt
	try:
		cd=client.containers.list()
		while(((reqcnt/20)+1)<int(len(cd))):
			try:
				cd=client.containers.list()
				container_list=[]
				ld=[]
				for i in cd:
				        dc={}
				        a=i.__dict__
					#print(a['attrs']['NetworkSettings']['Networks']['Ports'],'1111111111111111111')
				        dc[(a['attrs']['NetworkSettings']['Ports']['80/tcp'][0]['HostPort'])]=i
				        ld.append(dc)
				ld=sorted(ld,key=lambda i:(list(i.keys())[0]))
				for i in ld:
				        container_list.append(list(i.values())[0])
				print(container_list,"-----------------------------")
				container_list[-1].kill()
			except: pass
			cd=client.containers.list()
	except: pass
def htimer():
        global ACTS_IP
	cd=client.containers.list()
	container_list=[]
	ld=[]
	for i in cd:
		dc={}
		a=i.__dict__
		dc[(a['attrs']['NetworkSettings']['Ports']['80/tcp'][0]['HostPort'])]=i
		ld.append(dc)
	ld=sorted(ld)
	for i in ld:
		try:
			container_list.append(i.values()[0])
		except:
			pass
	print(container_list)
	print("hi")
	count=0
	try:
		for i in container_list:
			newport=8000+count
			new=80
			r = requests.get(ACTS_IP+':'+str(newport)+'/api/v1/_health')
			if(r.status_code==500):
				container_list[count].kill()
				container=client.containers.run('acts',ports={new:newport},detach=True)
				container_list[count]=container
			count+=1
	except:
		pass
	timer=threading.Timer(1.0, htimer)
	timer.start()
if __name__ == '__main__':
        timer=threading.Timer(0.0, htimer)
        timer.start()
        app.run(host='0.0.0.0', port=80)