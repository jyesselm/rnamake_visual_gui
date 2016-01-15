from __future__ import division, print_function
from visual import *
from visual.graph import *
import numpy as np
import wx

class GUIWindowNew(object):
    def __init__(self):
        L = 520
        Hgraph = 100

        self.window = window(width=2*(L+window.dwidth),
                             height=L+window.dheight+window.menuheight+Hgraph,
                             menus=True, title='RNAMake GUI',
                             style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)

        self.p = self.window.panel
        left = wx.Button(self.p, label='Mode', pos=(0,10))

        wx.StaticText(self.p, pos=(0,50), size=(100,20), label='Command:',
              style=wx.ALIGN_CENTRE | wx.ST_NO_AUTORESIZE)
        tc = wx.TextCtrl(self.p, pos=(100,50), value='',
            size=(800,20), style=wx.TE_MULTILINE)
        tc.SetInsertionPoint(len(tc.GetValue())+1) # position cursor at end of text
        tc.SetFocus()

        d = 20
        self.scene = display(window=self.window, x=10, y=100, width=1000, height=500,
                            center=(5,0,0), background=(1,1,1), ambient=color.gray(0.5))

        self.range = np.array([20,20,20])

    def listen(self):
        self.listen_for_keys()
        #self.listen_for_mouse()

    def listen_for_keys(self):
        if self.scene.kb.keys: # event waiting to be processed?
            key = self.scene.kb.getkey() # get keyboard info
            if key == 'z':
                self.scene.range = self.range/2
                self.range = self.range/2
            if key == 'x':
                self.scene.range = self.range*2
                self.range = self.range*2
            if key == 'a':
                self.scene.forward = self.scene.forward.rotate(angle=0.1, axis=(0,1,0))
            if key == 'w':
                self.scene.forward = self.scene.forward.rotate(angle=0.1, axis=(0,0,1))
            if key =='s':
                self.scene.forward = self.scene.forward.rotate(angle=0.1, axis=(1,0,0))

            if key =='left':
                self.scene.center = self.scene.center+np.array([1,0,0])
            if key =='right':
                self.scene.center = self.scene.center+np.array([-1,0,0])
            if key =='up':
                self.scene.center = self.scene.center+np.array([0,1,0])
            if key =='down':
                self.scene.center = self.scene.center+np.array([0,-1,0])

if __name__ == "__main__":
    win = GUIWindowNew()
    p = sphere(pos=[1,0,0], radius=1.5, color=color.cyan)
    while 1:
        rate(100)
        win.listen()