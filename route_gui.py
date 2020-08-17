import os, sys, time, threading, tkinter, PySimpleGUI as sg
from multiprocessing import Process

def node_layout(node):
    node_layout = [
        [sg.Button(node.hostname)],
        [sg.Button("Close")]
    ]
    return node_layout

class Node:
    def __init__(self, hostname:str, default:str=None):
        self.hostname = hostname
        self.connected = {}
        self.default = default
        self.state = "UP"
        self.routes = {}
        self.memory = []
    
    def show(self):
        window = sg.Window(self.hostname, node_layout(self), size=(120,70))
        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, 'Close'):
                break
        window.close()

    def __repr__(self):
        return f'<Node {self.hostname}>'

def network_layout(network):
    nodes = []
    for _, node in network.nodes.items():
        nodes.append(sg.Button(node.hostname))

    network_layout = [
        [sg.Text(network.name)],
        nodes,
        [sg.Button("Close")]
    ]
    return network_layout

class Network:
    def __init__(self, name):
        self.name = name
        self.nodes = {}

    def add_nodes(self, nodelist):
        for node in nodelist:
            self.nodes[node.hostname] = node

    def show(self):
        window = sg.Window(self.name, network_layout(self))
        while True:
            event, values = window.read()

            if event in (sg.WINDOW_CLOSED, 'Close'):
                break
            for node in self.nodes.keys():
                if event == node:
                    Process(target=self.nodes[node].show).start()
            
        window.close()

network = Network("net1")
network.add_nodes([Node("node1"), Node("node2")])
print(network.nodes)
network.show()