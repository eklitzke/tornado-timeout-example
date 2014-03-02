import datetime
import optparse
import socket
import time

import tornado.ioloop
import tornado.iostream


class Semaphore(object):

    def __init__(self, value):
        self.value = value

    def decrement(self):
        assert self.value > 0
        self.value -= 1

    def empty(self):
        return self.value == 0


class Worker(object):

    def __init__(self, io_loop, stream, semaphore):
        self.io_loop = io_loop
        self.stream = stream
        self.semaphore = semaphore

    def send_request(self):
        self.stream.write(b"GET / HTTP/1.0\r\nHost: www.uber.com\r\n\r\n")
        self.stream.read_until(b"\r\n\r\n", self.on_headers)

    def on_headers(self, data):
        headers = {}
        for line in data.split(b"\r\n"):
            parts = line.split(b":")
            if len(parts) == 2:
                headers[parts[0].strip()] = parts[1].strip()
        self.stream.read_bytes(int(headers[b"Content-Length"]), self.on_body)

    def on_body(self, unused_data):
        self.stream.close()
        self.semaphore.decrement()
        if self.semaphore.empty():
            self.io_loop.stop()


def magic(concurrency, timeout=1.0):
    timed_out = [False]
    loop = tornado.ioloop.IOLoop.instance()
    sem = Semaphore(concurrency)

    def on_timeout():
        timed_out[0] = True
        loop.stop()

    loop.add_timeout(datetime.timedelta(seconds=timeout), on_timeout)

    for x in xrange(concurrency):
        s = socket.socket()
        stream = tornado.iostream.IOStream(s)
        worker = Worker(loop, stream, sem)
        stream.connect(('www.uber.com', 80), worker.send_request)

    # start the loop
    t0 = time.time()
    loop.start()
    elapsed = time.time() - t0

    return elapsed, timed_out[0]

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-c', '--concurrency', type='int', default=16)
    parser.add_option('-t', '--timeout', type='float', default=1.0)
    opts, args = parser.parse_args()
    elapsed, timed_out = magic(opts.concurrency, opts.timeout)
    print '%s, took %1.3f seconds' % (
        'timed out' if timed_out else 'did not time out', elapsed)
