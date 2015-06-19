from uttt_gtk import uttt_gtk_main  # windows likes this to be first, I don't know why
import sys, getopt
from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager
from threading import Thread
from uttt_data import UTTTData
from uttt_websocket import uttt_websocket_main, uttt_websocket_create
from uttt_cli import uttt_cli_main
from uttt_pygame import uttt_pygame_main
from uttt_ai import uttt_ai_main

if sys.platform == 'win32':
    import multiprocessing.reduction    # make sockets pickable/inheritable

### make game data accessible to all processes
class UTTTDataManager(BaseManager):
    pass
    
UTTTDataManager.register("UTTTData", UTTTData)


g_short_opts = 'hu:p:al:'
g_long_opts = ["help", "username=", "password=", "ai", "ai-level="]

def usage():
    print "usage: %s %s %s" % (sys.argv[0], g_short_opts, g_long_opts)

def parse_args():
    arguments = { 'username':  '',
                  'password': '',
                  'ai': False,
                  'ai-level': 7,
                  }
    try:
        opts, args = getopt.getopt(sys.argv[1:], g_short_opts, g_long_opts)
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)

    for o, a in opts:
        if o in ("-u", "--username"):
            arguments['username'] = a
        elif o in ("-p", "--password"):
            arguments['password'] = a
        elif o in ("-a", "--ai"):
            arguments['ai'] = True
        elif o in ("-l", "--ai-level"):
            arguments['ai-level'] = int(a)
        elif o in ("-h", "--help"):
            usage()
            sys.exit(1)
        else:
            assert False, "Unhandled option: '%s:%s'" % (o, a)

    return arguments


def main():
    arguments = parse_args()
    
    ### A Queue of messages to send to the web socket
    send_queue = Queue()
    ### A Queue of messages to send/receive to/from the ai
    ai_send_queue = Queue()
    ai_recv_queue = Queue()
    
    ### make game data accessible to all processes
    uttt_data_manager = UTTTDataManager()
    uttt_data_manager.start()
    data = uttt_data_manager.UTTTData()

    ### start processes
    processes = []

    ### websocket receiver
    t = Process(target=uttt_websocket_main, args=(data, send_queue))
    t.start()
    processes.append(t)
    
    send_queue.put("ping")

    if arguments['username'] and arguments['password']:
        text = data.SendLogin(arguments['username'], arguments['password'])
        send_queue.put(text)

    # ### command line interface
    # u = Thread(target=uttt_cli_main, args=(data, send_queue))
    # u.start()
    # processes.append(u)

    ### pygame interface
    v = Process(target=uttt_pygame_main, args=(data, send_queue, arguments['ai'], arguments['ai-level'], ai_send_queue, ai_recv_queue))
    v.start()
    processes.append(v)

    ### pygtk interface
    if not arguments['ai']:
        print "GTK startup will be delayed 20 seconds due to dbus not working in a separate process."
        w = Process(target=uttt_gtk_main, args=(data, send_queue))
        w.start()
        processes.append(w)
    else:
        w = None

    ### ai process
    if arguments['ai']:
        x = Process(target=uttt_ai_main, args=(data, ai_send_queue, ai_recv_queue))
        x.start()
        processes.append(x)
    else:
        x = None
    
    ### wait for end of processes
    if t:
        t.join()
        print "websocket joined."
    # u.join()
    if v:
        v.join()
        print "pygame joined."
    if w:
        w.join()
        print "gtk joined."
    if x:
        x.join()
        print "ai joined."
    return

if __name__ == "__main__":
    main()

