#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import socket
import config

__all__ = ['send', 'recv', 'permit']

conf = config.get_config()
server_addr = (
    conf.get('limit', 'server_host'),
    conf.getint('limit', 'server_port'),
)
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.settimeout(conf.getint('limit', 'timeout') / 1000.0)


def send(data):
    send_len = udp_socket.sendto(data, server_addr)
    if send_len == len(data):
        return True
    else:
        return False


def recv(size=1024):
    data, _ = udp_socket.recvfrom(size)
    return data


def permit(uid):
    send(uid)
    data = recv()
    return data
