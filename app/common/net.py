import ping

__author__ = 'Lesko'
# Documentation is like sex.
# When it's good, it's very good.
# When it's bad, it's better than nothing.
# When it lies to you, it may be a while before you realize something's wrong.


def is_up(ip, timeout=1, psize=64):
    ah = ping.do_one(dest_addr=ip, timeout=timeout, psize=psize)
    return (True if ah is not None else False,
            ah if ah is not None else None)


if __name__ == '__main__':
    print is_up("192.168.1.100")
