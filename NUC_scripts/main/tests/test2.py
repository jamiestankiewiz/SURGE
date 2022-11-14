import subprocess as sp
from time import sleep

extProc = sp.Popen(['python','test1.py']) # runs myPyScript.py 

status = sp.Popen.poll(extProc) # status should be 'None'
print(status)
sleep(3)
sp.Popen.terminate(extProc) # closes the process

status = sp.Popen.poll(extProc) # status should now be something other than 'None' ('1' in my testing)
print(status)