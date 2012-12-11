'''
Created on Jan 25, 2012

@author: pavel
'''
# from pollingthread import PollingThread

# if __name__ == '__main__':
#     polling = PollingThread()
#     polling.start()

#     while(polling.isAlive()):
#         try:
#             polling.join(1)
#         except KeyboardInterrupt:
#             polling.stop()

from corehandler import corehandler
c = corehandler(None, {"configfile": "config/coreconfig.txt"})
while c.isAlive():
    try:
        c.join(1)
    except KeyboardInterrupt:
        c.stop()
print "END"
