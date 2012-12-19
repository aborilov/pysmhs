'''
Created on Jan 25, 2012

@author: pavel
'''

from corehandler import corehandler
c = corehandler(None, {"configfile": "config/coreconfig.txt"})
while c.isAlive():
    try:
        c.join(1)
    except KeyboardInterrupt:
        print 'Have ctrl-c'
        c.stop()
print "END"
