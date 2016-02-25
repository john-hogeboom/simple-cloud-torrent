import subprocess
from subprocess import Popen,PIPE
import os
import ConfigParser
import csv
import sys
import shlex
import re
import unicodedata
import time
import shutil
from distutils.dir_util import copy_tree
import zipfile

interval=240
delugePath=''
megatoolsPath=''
zip7Path=""
thisdir=False#os.getcwd()
mstart='magnet:?xt=urn:btih:'
completedStatus={}
uploadedStatus={}
zipFiles=False
finishedDownloadText='finisheddownloadasdfjhli'

#magnetPattern=re.compile('^[A-F\d]*\Z')
#def verifyMagnet(mlink):
#	magnetPattern.match(mlink) is not None
def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))
def getScriptPath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))
def clearTemp():
	folder=thisdir+'/temp'
	shutil.rmtree(folder)
	os.makedirs(folder)
def copyAllToTemp(dir):
	folder=thisdir+'/temp'
	copy_tree("\\\\?\\"+os.getcwd() +dir, folder)
def copyFileToTemp(file):
	folder=thisdir+'/temp'
	shutil.copyfile("\\\\?\\"+os.getcwd() +file,folder)
def replaceStatusDirectory(parentdir,text):
	if os.path.exists(parentdir+'/status'):
		for file in os.listdir(parentdir+'/status'):
			print file
			os.remove(parentdir+'/status/'+file)
	else:
		os.mkdir(parentdir+'/status')
	file = open(parentdir+'/status'+'/'+text, "w")
	file.write("")
	file.close()

# def unregisterUploadCompleted(hash):
	# for dir in os.listdir(thisdir+'/downloads'):
		# if dir == hash:
			# if os.path.isfile(thisdir+'/downloads/'+hash+'/'+finishedDownloadText):
				# os.remove(thisdir+'/downloads/'+hash+'/'+finishedDownloadText)
				
#has bug where if someone later wants to dl this, it's registered as finished. Remove finished torrents and associated files? Maintain user specific files listing already uploaded files?
# def registerUploadsCompleted():
	# for dir in os.listdir(thisdir+'/downloads'):
		# if dir in uploadedStatus:
			# file = open(thisdir+'/downloads/'+dir+'/'+finishedDownloadText, "w")
			# file.write("")
			# file.close()

def ensureFolderExists(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)
def registerDownloadCompleted(hash,username):
	folder=thisdir+'/users/'+username
	ensureFolderExists(folder)
	folder=folder+'/completedDownloads'
	ensureFolderExists(folder)
	file = open(folder+'/'+hash, "w")
	file.write("")
	file.close()
def fileAlreadyDownloaded(hash,username):
	folder=thisdir+'/'+username+'/completedDownloads'
	if os.path.exists(folder):
		if hash in os.listdir(folder+'/'+hash):
			return True
	return False
def strToValidFilename(value):
	value=unicode(value, "utf-8")
	value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
	value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
	re.sub('[-\s]+', '-', value)
	value=value.replace(" ","_")
	return value
def createTorrentFromMagnet(magnetstr,hash):
	
	print 'adding magnet grsehrtsh'
	olddir=os.getcwd()
	#os.chdir(delugePath)
	#print 'afklwefg '+str(subprocess.check_output(["deluge-console.exe"]))
	os.chdir(thisdir)
	
	todl='downloads/'+hash
	if not os.path.exists(todl):
		print 'making dir '+todl
		os.makedirs(todl)
	else:
		print 'folder already exists, not adding torrent'
		return False
	#print 'types: '+str(type(delugePath))+' '+str(type(magnetstr))+' '+str(type(hash))
	#'"'+delugePath+'/deluge-console.exe" add -p downloads/
	#args=shlex.split('"'+delugePath+'/deluge-console.exe" add -p downloads/'+hash+' "'+magnetstr+'"')
	
	args=shlex.split('"'+delugePath+'deluge-console" add -p "'+thisdir+'/downloads/'+hash+'" '+magnetstr)
	
	print '\nadding torrent: '+str(args)
	process = Popen(args, stdout=PIPE, stderr=PIPE)
	stdout, stderr = process.communicate()
	#addtorrent=str(subprocess.check_output(args))
	print '\noutput: '+stdout+'\n'+stderr+'^'
	os.chdir(olddir)
	return True
def megaUpdateFiles(username,password,hash):
	olddir=os.getcwd()
	copydir='downloads/'+hash
	
	if fileAlreadyDownloaded(hash,username):
		print 'already uploaded this file '+str(os.listdir(copydir))
		return
	
	name=completedStatus[hash][0]
	finishedTorrenting=completedStatus[hash][1]
	print 'creating mega folder for torrent'
	args=shlex.split('"'+megatoolsPath+'megamkdir" -u '+username+' -p '+password+' /Root/TorrentToCloud/'+strToValidFilename(name)+'_'+hash)
	print 'args2:'+str(args)
	process = Popen(args, stdout=PIPE, stderr=PIPE)
	stdout2, stderr2 = process.communicate()
	print '\noutput: '+stdout2+'\n'+stderr2+'^'
	
	print 'removing mega folder for status'
	args=shlex.split('"'+megatoolsPath+'megarm" -u '+username+' -p '+password+' /Root/TorrentToCloud/'+strToValidFilename(name)+'_'+hash+'/status')
	print 'args2:'+str(args)
	process = Popen(args, stdout=PIPE, stderr=PIPE)
	stdout2, stderr2 = process.communicate()
	print '\noutput: '+stdout2+'\n'+stderr2+'^'
	
	if not finishedTorrenting:
		print 'creating mega folder for status'
		args=shlex.split('"'+megatoolsPath+'megamkdir" -u '+username+' -p '+password+' /Root/TorrentToCloud/'+strToValidFilename(name)+'_'+hash+'/status')
		print 'args2:'+str(args)
		process = Popen(args, stdout=PIPE, stderr=PIPE)
		stdout2, stderr2 = process.communicate()
		print '\noutput: '+stdout2+'\n'+stderr2+'^'
		
		print stdout2+stderr2
		if os.path.exists('downloads/'+hash+'/status'):
			print 'adding new status file'
			args=shlex.split('"'+megatoolsPath+'megacopy" -u '+username+' -p '+password+' --remote  /Root/TorrentToCloud/'+strToValidFilename(name)+'_'+hash+'/status --local '+'downloads/'+hash+'/status')
			print 'args3:'+str(args)
			process = Popen(args, stdout=PIPE, stderr=PIPE)
			stdout2, stderr2 = process.communicate()
			print stdout2+stderr2
			print '\noutput: '+stdout2+'\n'+stderr2+'^'
	else:
		print 'srthiorsiotrsh'
		# clearTemp()
		# print 'copying to temp'
		# for file in os.listdir(copydir):
			# if not file=='status':
				# if os.path.isfile(copydir+'/'+file):
					# print 'copy file '+copydir+'/'+file
					# copyFileToTemp(copydir+'/'+file)
					# #copyAllToTemp(copydir)
				# if os.path.isdir(copydir+'/'+file):
					# print 'copy folder '+copydir+'/'+file
					# copyAllToTemp(copydir+'/'+file)
		# zipf = zipfile.ZipFile('Python.zip', 'w')
		# zipdir(copydir, zipf)
		# zipf.close()
		os.chdir(copydir)
	
		print 'adding the final files'
		if not zipFiles:
			args=shlex.split('"'+megatoolsPath+'megacopy" -u '+username+' -p '+password+' --remote  /Root/TorrentToCloud/'+strToValidFilename(name)+'_'+hash+' --local .')#"'+copydir+'"')
			print 'args3:'+str(args)
			process = Popen(args, stdout=PIPE, stderr=PIPE)
			stdout2, stderr2 = process.communicate()
			#print stdout2+stderr2
			print '\noutput: '+stdout2+'\n'+stderr2+'^'
		else:
			zipname=None
			for file in os.listdir('.'):
				if not file=='status':
					args=shlex.split('"'+zip7Path+'7z" a "'+thisdir+'/temp/'+name+'.zip" "'+file+'"')#"'+copydir+'"')
					print 'args3:'+str(args)
					process = Popen(args, stdout=PIPE, stderr=PIPE)
					stdout2, stderr2 = process.communicate()
					print '\noutput: '+stdout2+'\n'+stderr2+'^'
					zipname=thisdir+'/temp/'+name+'.zip'
					# if os.path.isfile(file):
						# print 'adding the final files'
						# args=shlex.split('"'+megatoolsPath+'/megaput" -u '+username+' -p '+password+' --path  /Root/TorrentToCloud/'+strToValidFilename(name)+'_'+hash+'/'+file+' "'+copydir+'/'+file+'"')
						# print 'args3:'+str(args)
						# process = Popen(args, stdout=PIPE, stderr=PIPE)
						# stdout2, stderr2 = process.communicate()
						# print stdout2+stderr2
						# print '\noutput: '+stdout2+'\n'+stderr2+'^'
					# if os.path.isdir(file):
						
						# print 'adding the final files'
						# args=shlex.split('"'+megatoolsPath+'/megacopy" -u '+username+' -p '+password+' --remote  /Root/TorrentToCloud/'+strToValidFilename(name)+'_'+hash+' --local "'+copydir+'/'+file+'"')
						# print 'args3:'+str(args)
						# process = Popen(args, stdout=PIPE, stderr=PIPE)
						# stdout2, stderr2 = process.communicate()
						# print stdout2+stderr2
						# print '\noutput: '+stdout2+'\n'+stderr2+'^'
					# print 'fileesrthsrthre:'+file
			if not zipname==None:
				args=shlex.split('"'+megatoolsPath+'megaput" -u '+username+' -p '+password+' --path  /Root/TorrentToCloud/'+strToValidFilename(name)+'_'+hash+' "'+zipname+'"')#"'+copydir+'"')
				print 'args3:'+str(args)
				process = Popen(args, stdout=PIPE, stderr=PIPE)
				stdout2, stderr2 = process.communicate()
				print '\noutput: '+stdout2+'\n'+stderr2+'^'
				os.remove(zipname)
		registerDownloadCompleted(hash,username)
		
	os.chdir(olddir)
def processMagnetLink(username,password,magnet):
	endhash=magnet.find('&')
	if(endhash==-1):
		endhash=len(magnet)
	hash=magnet[magnet.index(mstart)+len(mstart):endhash]
	print 'hash:'+hash
	isNew=createTorrentFromMagnet(magnet,hash)
	if not isNew:
		print 'torrent not new '+str(hash)+str(completedStatus)
		if hash in completedStatus:
			#add files to mega
			print 'mega update files'
			megaUpdateFiles(username, password, hash)
def processUser(username,password):
	print username+" , "+password
	print "thisdir "+thisdir
	#os.chdir(delugePath)
	#args=shlex.split('"'+delugePath+'deluge-console"')
	#print 'args '+str(args)
	#print 'afklwefg \n'+str(args)+'\n'+str(subprocess.check_output(args))
	#os.chdir(megatoolsPath)
	print os.getcwd()
	args=shlex.split('"'+megatoolsPath+'megals" -u '+username+' -p '+password+' --reload')
	print args
	
	process = Popen(args, stdout=PIPE, stderr=PIPE)
	stdout, stderr = process.communicate()
	
	for s in stderr.split('\n'):
		s=s[:-2]
		if len(s)>10 and len(s)<1500 and mstart in s:
			print 'errpart is:'+s+'^'
			print  'extracted magnet:^'+s[s.index("invalid '")+9:]+'^'#'##'+s+'@@\n***********\n'
			magnet=s[s.index("invalid '")+9:]
			processMagnetLink(username,password,magnet)
	megals=stdout#str(subprocess.check_output(args))
	print '\ntestfdghsru7456\n'
	hasFolder=False
	hasMagnetFile=False
	for s in megals.split('\n'):
		s=s[:-1]
		print '$$'+s+'\n^^^^^^^^\n'
		if s=='/Root/TorrentToCloud':
			hasFolder=True
		if s=='Root/TorrentToCloud/magnets.txt':
			hasMagnetFile=True
		if '/Root/TorrentToCloud' in s:
			if 'magnet:?xt=urn:btih:' in s:
				magnet=s[len('Root/TorrentToCloud/ '):]
				print 'magnet is '+magnet
				print 'len'+str(len(magnet))
				processMagnetLink(username,password,magnet)
				
	if not hasFolder: #make the folder if it does not exist
		args=shlex.split('"'+megatoolsPath+'megamkdir" -u '+username+' -p '+password+' '+'/Root/TorrentToCloud')
		print args
		megamkdir=str(subprocess.check_output(args))
		print megamkdir
	# if not hasMagnetFile:
		# print os.getcwd()
		# print 'thisdir2 '+thisdir
		# args=shlex.split('megaput --path /Root/TorrentToCloud/magnets.txt -u '+username+' -p '+password+' "' +thisdir+'/magnets.txt"')
		# print 'attempt make magnetstxt'
		# megaput=str(subprocess.check_output(args))
		# print megaput
		# args=shlex.split('megals -u '+username+' -p '+password)
		# megals=str(subprocess.check_output(args))
		# print megals
	# else:
		# args=shlex.split('megaget -u '+username+' -p '+password+' /Root/TorrentToCloud/magnets.txt')
		# megaget=str(subprocess.check_output(args))

def findHashEnd(astr):
	index=0
	for c in astr:
		if not c.isalnum():
			return index
		index+=1
	return index-1

def updateTorrentStatus():
	args=shlex.split('"'+delugePath+'deluge-console" info')
	
	print '\ntorrent info: '+str(args)
	process = Popen(args, stdout=PIPE, stderr=PIPE)
	stdout, stderr = process.communicate()
	print 'stdout:'+stdout
	if len(stdout)<1000 and 'No connection could be made' in stdout:
		return
	#addtorrent=str(subprocess.check_output(args))
	name=''
	id=''
	size=''
	finished=False
	parts=stdout.split('\nName: ')
	for part in parts:
		print '\n$$$$$$$$$$$$\n'+part
		if len(part)>50:
			endline=part.index('\n')
			if '\r\n' in part:
				endline=part.index('\r\n')
			name=part[:endline]
			#print 'name:'+name+'^'
			next=part[len(name):]
			print 'ni pre:'+next
			print 'nextinfo:'+str(next.index('ID: ')+len('ID: '))+'^ '#+str(next.index('\n'))+'^'
			next2=next[next.index('ID: ')+len('ID: '):]
			id=next2[:findHashEnd(next2)]#next.index('\n')-1]
			#print 'id:'+id+'^'
			next=next[next.index('Size: '):]
			size=next[next.index('Size: ')+len('Size: '):next.index(' Ratio')]
			#print 'size:'+size+'^'
			sparts=size.split('/')
			finished=sparts[0]==sparts[1]
			
			progress='unknown'
			if 'Progress: ' in next:
				next=next[next.index('Progress: ')+len('Progress: '):]
				progress=next[:next.index('[')-1]
			#print 'finished: '+str(finished)
			tfolder='downloads/'+id
			print 'tfolder: '+tfolder
			if os.path.exists(tfolder):
				print 'replacing status directory '+tfolder+' '+size
				replaceStatusDirectory(tfolder,progress)
				
			completedStatus[id]=[name,finished]
		#if not part.index('')
	#print '\ninfo: '+stdout+'\n'+stderr+'^'
	#register this torrent as having been added


		
print "\n\n*************\n\n"
thisdir=getScriptPath()
Config = ConfigParser.ConfigParser()
Config.read("config.txt")
print Config.sections()
global delugePath
delugePath=Config.get('file','DelugeInstall')
if delugePath==' ' or delugePath=='':
	delugePath='';
else:
	delugePath+='/'
global megatoolsPath
megatoolsPath=Config.get('file','MegatoolsInstall')
if megatoolsPath==' ' or megatoolsPath=='':
	megatoolsPath='';
else:
	megatoolsPath+='/'
global interval
interval=Config.getint('other','interval_seconds')
print interval+5
global zipFiles
zipFiles=Config.getboolean('other','zip_files')
print 'zipfiles:'+str(zipFiles)
global zip7Path
zip7Path=Config.get('file','7ZipInstall')
if zip7Path==' ' or zip7Path=='':
	zip7Path='';
else:
	zip7Path+='/'
print '7zpath: '+zip7Path
ensureFolderExists(thisdir+'/downloads')
ensureFolderExists(thisdir+'/temp')
while True:
	start=time.time()
	print 'starting check at '+str(start)
	updateTorrentStatus()
	with open('accounts.csv', 'rb') as f:
		reader = csv.reader(f)
		count=0
		for row in reader:
			if count>0:
				pass
				processUser(row[0],row[1])
			count+=1
	#registerUploadsCompleted()
	print 'waiting for next check'
	while time.time()-start < interval:
		print str(time.time()-start)+'/'+str(interval)
		time.sleep(5)

