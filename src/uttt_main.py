from uttt_gtk import uttt_gtk_main  # windows likes this to be first, I don't know why
import sys
from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager
from threading import Thread
from uttt_data import UTTTData
from uttt_websocket import uttt_websocket_main, uttt_websocket_create
from uttt_cli import uttt_cli_main
from uttt_pygame import uttt_pygame_main

if sys.platform == 'win32':
    import multiprocessing.reduction    # make sockets pickable/inheritable

### make game data accessible to all processes
class UTTTDataManager(BaseManager):
    pass
    
UTTTDataManager.register("UTTTData", UTTTData)

def main():
    ### A Queue of messages to send to the web socket
    send_queue = Queue()
    
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

    # ### command line interface
    # u = Thread(target=uttt_cli_main, args=(data, send_queue))
    # u.start()
    # processes.append(u)

    ### pygame interface
    v = Process(target=uttt_pygame_main, args=(data, send_queue))
    v.start()
    processes.append(v)

    ### pygtk interface
    print "GTK startup will be delayed 20 seconds due to dbus not working in a separate process."
    w = Process(target=uttt_gtk_main, args=(data, send_queue))
    w.start()
    processes.append(w)
    
    ### wait for end of processes
    t.join()
    print "websocket joined."
    # u.join()
    v.join()
    print "pygame joined."
    w.join()
    print "gtk joined."
    return

if __name__ == "__main__":
    main()

