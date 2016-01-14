from __future__ import division, print_function
from visual import *
from visual.graph import *
import wx

class GUIWindowNew(object):
    def __init__(self):
        L = 520
        Hgraph = 100

        self.window = window(width=2*(L+window.dwidth),
                             height=L+window.dheight+window.menuheight+Hgraph,
                             menus=True, title='Widgets',
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
        self.disp = display(window=self.window, x=10, y=100, width=1000, height=500)


if __name__ == "__main__":
    win = GUIWindowNew()
    p = sphere(pos=[1,0,0], radius=1.5, color=color.cyan)
