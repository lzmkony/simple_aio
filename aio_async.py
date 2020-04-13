import socket
import time
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from typing import Tuple, Callable, List, Any, Awaitable, Union
from urllib.parse import urlparse

selector = DefaultSelector()
stopped = False

class Future:
    '''封装一个Future 对象
    '''
    def __init__(self):
        self.result:Any = None
        self._callbacks:List[Callable] = []

    def add_callback(self, fn: Callable) -> None:
        '''添加一个callback 函数
        '''
        self._callbacks.append(fn)

    def set_result(self, result:Any) -> None:
        '''设置一个结果
        '''
        self.result = result
        for callback in self._callbacks:
            callback(self)

    def __await__(self):
        '''await 的出现使得__await__函数变成一个生成器
        '''
        # 外面使用await把f实例本身返回
        yield self
        return self.result


async def connect(sock: socket.socket, address: Tuple) -> None:
    f = Future()
    # 将socket 设置为非阻塞模式
    sock.setblocking(False)
    try:
        sock.connect(address)
    except BlockingIOError:
        pass

    def on_connected():
        f.set_result(None)

    selector.register(sock.fileno(), EVENT_WRITE, on_connected)
    await f
    # 移除监听
    selector.unregister(sock.fileno())

async def read(sock: socket.socket) -> bytes:
    '''从 socket 中读取bytes
    '''
    f = Future()

    def on_readable():
        f.set_result(sock.recv(4096))

    selector.register(sock.fileno(), EVENT_READ, on_readable)
    chunck = await f
    # 移除监听
    selector.unregister(sock.fileno())
    return chunck

async def read_all(sock: socket.socket) -> bytes:
    '''循环读一个socket 信息
    '''
    response = []
    chunk = await read(sock)
    while chunk:
        response.append(chunk)
        chunk = await read(sock)
    return b"".join(response)

class Crawler:
    '''创建一个爬虫类
    '''
    def __init__(self, url) ->None:
        self.xparse(url)
        self.response: bytes = b""

    def xparse(self, url):
        xhttp = urlparse(url)
        self.url = xhttp.path
        self.hostname = xhttp.hostname
        self.port = xhttp.port if xhttp.port else 80


    async def fetch(self) -> None:
        '''模拟请求
        '''
        sock = socket.socket()
        await connect(sock, (self.hostname, self.port))
        get = "GET {0} HTTP/1.0\r\nHost:{1}\r\n\r\n".format(self.url, self.hostname)
        sock.send(get.encode('ascii'))
        self.response = await read_all(sock)

class Task:
    def __init__(self, coro) -> None:
        self.coro = coro
        # 激活Task包裹的生成器
        self.step(None)

    def step(self, future: Future) -> None:
        try:
            # print(dir(self.coro))
            next_future = self.coro.send(future.result if future else None)
        except StopIteration:
            return
        next_future.add_callback(self.step)


async def get_url(url):
    '''
    '''
    crawler = Crawler(url)
    await crawler.fetch()
    print(crawler.response)

def loop_until() -> None:
    '''
    '''
    while True:
        events = selector.select()
        if not events:
            time.sleep(0.01)
            continue
        for event_key, event_mask in events:
            callback = event_key.data
            callback()

if __name__ == "__main__":
    urls_todo = {"http://127.0.0.1:8888/1", "http://127.0.0.1:8888/2"}

    for url in urls_todo:
        Task(get_url(url))
    loop_until()
