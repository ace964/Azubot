"""
    Interface for Controllers
    functionality described in ps4.py ord xbox.py
"""
class IController:
    def start(self):
        raise NotImplementedError

    def getActions(self):
        raise NotImplementedError
