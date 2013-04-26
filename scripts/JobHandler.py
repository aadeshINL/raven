'''
Created on Mar 5, 2013

@author: crisr
'''
import Queue as queue
import subprocess
import os
import signal

class ExternalRunner:
  def __init__(self,command,workingDir,output=None):
    self.command    = command
    if    output!=None: 
      self.output = output
      self.identifier =  str(output).split("~")[1]
    else: 
      os.path.join(workingDir,'generalOut')
    self.workingDir = workingDir
    
  def isDone(self):
    self.process.poll()
    if self.process.returncode != None:
      return True
    else:
      return False
  
  def start(self):
    oldDir = os.getcwd()
    os.chdir(self.workingDir)
    localenv = dict(os.environ)
    localenv['PYTHONPATH'] = ''
    outFile = open(self.output,'w')
    self.process = subprocess.Popen(self.command,shell=True,stdout=outFile,stderr=outFile,cwd=self.workingDir,env=localenv)
    os.chdir(oldDir)
  
  def kill(self):
    #In python 2.6 this could be self.process.terminate()
    print "Terminating ",self.process.pid,self.command
    os.kill(self.process.pid,signal.SIGTERM)    

class JobHandler:
  def __init__(self):
    self.runInfoDict       = {}
    self.external          = True
    self.mpiCommand        = ''
    self.threadingCommand  = ''
    self.submitDict = {}
    self.submitDict['External'] = self.addExternal
    self.submitDict['Internal'] = self.addInternal
    self.externalRunning        = []
    self.internalRunning        = []
    self.running = []
    self.queue = queue.Queue()
    self.next_id = 0
    self.num_submitted = 0
    
  def initialize(self,runInfoDict):
    self.runInfoDict = runInfoDict
    if self.runInfoDict['ParallelProcNumb'] !=1:
      self.mpiCommand = self.runInfoDict['ParallelCommand']+' '+self.runInfoDict['ParallelProcNumb']
    if self.runInfoDict['ThreadingProcessor'] !=1:
      self.threadingCommand = self.runInfoDict['ThreadingCommand'] +' '+self.runInfoDict['ThreadingProcessor']
    #initialize PBS
    self.running = [None]*self.runInfoDict['batchSize']

  def addExternal(self,executeCommand,outputFile,workingDir):
    #probably something more for the PBS
    command = ''
    if self.mpiCommand !='':
      command += self.mpiCommand+' '
    if self.threadingCommand !='':
      command +=self.threadingCommand+' '
    command += executeCommand
    self.queue.put(ExternalRunner(command,workingDir,outputFile))
    self.num_submitted += 1

  def isFinished(self):
    if not self.queue.empty():
      return False
    for i in range(len(self.running)):
      if self.running[i] and not self.running[i].isDone():
        return False
    return True

  def getFinished(self):
    #print("getFinished "+str(self.running)+" "+str(self.queue.qsize()))
    finished = []
    for i in range(len(self.running)):
      if self.running[i] and self.running[i].isDone():
        finished.append(self.running[i])
        self.running[i] = None
    if self.queue.empty():
      return finished
    for i in range(len(self.running)):
      if self.running[i] == None and not self.queue.empty(): 
        item = self.queue.get()          
        command = item.command
        command = command.replace("%INDEX%",str(i))
        command = command.replace("%INDEX1%",str(i+1))
        command = command.replace("%CURRENT_ID%",str(self.next_id))
        self.running[i] = item
        self.running[i].start()
        self.next_id += 1

    return finished

  def getNumSubmitted(self):
    return self.num_submitted

  def addInternal(self):
    return
  
  def terminateAll(self):
    #clear out the queue
    while not self.queue.empty():
      self.queue.get()
    for i in range(len(self.running)):
      self.running[i].kill()


