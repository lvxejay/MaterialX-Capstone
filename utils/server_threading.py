# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
import threading

from .io import IO
from .. import conf


# -----------------------------------------------------------------------------
# Launch thread
# -----------------------------------------------------------------------------

#TODO; Create Threading Decorator to autowrap/thread any function
def thread(func):
    def generate_thread(*args, **kwargs):
        if conf.threading_halt is True:
            return
        if conf.vv: IO.debug("Starting background processing")
        arguments = func(kwargs.get("arguments"))
        if arguments is None:
            arguments = ()
        argwrap = args[0], len(conf.server_threads), arguments
        new_thread = threading.Thread(target=thread_starter_func, args=argwrap)
        new_thread.daemon = True
        try:
            new_thread.start()
            conf.server_threads.append(new_thread)
        except Exception as e:
            print("exception starting thread:")
            print(str(e))
            return False
        return True
    return generate_thread


def launch_background_thread(func, arguments=None):
    if conf.threading_halt == True:
        return
    if conf.vv: print("Starting background")

    if arguments == None:
        arguments = ()

    # NOTE! not a stable way to get thread ID, not an atomic operation..
    # but up until now, everything should be on the same sequence
    argwrap = (func, len(conf.server_threads), arguments)

    new_thread = threading.Thread(target=thread_starter_func,args=argwrap)
    new_thread.daemon = True

    # protect starting of a thread, pass to UI if failed
    # note: this is only for starting a thread, not capturing
    # if the function itself err's out
    try:
        new_thread.start()
        conf.server_threads.append(new_thread)
    except Exception as e:
        print("exception starting thread:")
        print(str(e))
        return False

    # do NOT do anything like this, will block thread
    # t1.join()

    return True

# wrap all async calls to handle thread tracking
def thread_starter_func(func,ID,args):

    # run the function requested, must be safe
    # print("Wrapper for thread:")
    try:
        print(args)
        func(args)
    except Exception as e:
        print("!! Background thread exception:")
        print("\t"+str(e))

    # now run the completion
    # remove this thread from the list:
    # print("Pop the thread.. not actually doing this yet")
    #conf.server_threads[ID-1]


# refresh the list of threads in case they are stale
def update_threads():

    tmp = []
    for t in conf.server_threads:
        if t.isAlive() == True: tmp.append(t)

    conf.server_threads = tmp
