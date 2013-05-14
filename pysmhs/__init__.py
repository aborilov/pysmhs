'''
Created on Jan 25, 2012

@author: pavel
'''
import signal

if __name__ == '__main__':
    from corehandler import corehandler
    c = corehandler(None, {"configfile": "config/coreconfig.txt"})

    def stop(signum, stackframe):
        print "Got signal: %s" % signum
        print "STOP"
        c.stop()
    signal.signal(signal.SIGINT, stop)
    c.start()
    # while c.isAlive():
    #     try:
    #         c.join(1)
    #     except KeyboardInterrupt:
    #         c.stop()
    print "END"
