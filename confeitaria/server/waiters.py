import socket
import errno
import contextlib

def wait_server_up(address, port, tries=1000, timeout=1):
    """
    This function blocks the execution until connecting successfully to the
    given address and port, or until an error happens - in this case, it will
    raise the exception.

    If an conection is refused, this error will be ignored since it probably
    means the server is not up yet. However, this error will only be ignored
    for <tries> times (by default 1000). Once the connection is refuses for more
    than <tries> times, an exception will be raises.
    """
    for i in xrange(tries):
        s = socket.socket()
        s.settimeout(timeout)
        with contextlib.closing(s):
            try:
                s.connect((address, port))
                break
            except socket.error as e:
                if e.errno != errno.ECONNREFUSED:
                    raise
    else:
        raise Exception(
            'Connection to server failed after {0} attempts'.format(tries)
        )

def wait_server_down(address, port, tries=1000, timeout=0.0001):
    """
    This function blocks until the given port is free at the given address, or
    until an error occurrs, in which case the exception is raised.

    If an conection is refused or reset, this error will be ignored since it
    probably means respectively the server is not up (as excepted) or just went
    down during the connection, which is acceptable.

    The funcion allows for defining the socket timeout. Setting a low value made
    this function faster than setting none.
    """
    for i in xrange(tries):
        s = socket.socket()
        with contextlib.closing(s):
            try:
                s.settimeout(timeout)
                s.connect((address, port))
            except socket.timeout:
                continue
            except socket.error as e:   
                if e.errno in (errno.ECONNREFUSED, errno.ECONNRESET):
                    break
                elif e.errno == errno.ETIMEDOUT:
                    continue
                else:
                    raise
    else:
        raise Exception(
            'Server stayed up after {0} connection attempts. '
            'May it be running from a process outside the tests?'.format(tries)
        )

