from __future__ import division, print_function
from visual import *
from visual.graph import *
import numpy as np
import wx

class GUIWindowFunction(object):

    def listen(self, scene):
        pass

class DrawFunction(GUIWindowFunction):
    def __init__(self):
        self.activated = 1
        self.points = []
        self.lines = []

    def listen_for_keys(self, key):
        if key == 'd':
            if len(self.points) != 0:
                last = self.points.pop()
                last.visible = False
                del last
            if len(self.lines) != 0:
                last_l = self.lines.pop()
                last_l.visible = False
                del last_l

    def listen_for_mouse(self, scene):
        if scene.mouse.events:
            m1 = scene.mouse.getevent() # get event

            if m1.pick is None:
                p = sphere(pos=m1.pos, radius=1.5, color=color.cyan)
                self.points.append(p)

                """reg_points = []
                for p in points:
                    reg_points.append(p.pos)
                f = open("points.pdb", "w")

                str = basic_io.points_to_pdb_str(reg_points)
                f.write(str)
                f.close()"""

                if len(self.points) > 1:
                    line = cylinder(pos=self.points[-2].pos,
                                    axis=p.pos - self.points[-2].pos,
                                    color=color.black)
                    self.lines.append(line)

    def listen(self, scene, key):
        self.listen_for_keys(key)
        self.listen_for_mouse(scene)


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
        self.functions = []

    def listen(self):
        key = self.listen_for_keys()
        #self.listen_for_mouse()

        for f in self.functions:
            if not f.activated:
                continue
            f.listen(self.scene, key)

    def listen_for_keys(self):
        if self.scene.kb.keys: # event waiting to be processed?
            key = self.scene.kb.getkey() # get keyboard info
            if key == 'z':
                self.scene.range = self.range/2
                self.range = self.range/2
            elif key == 'x':
                self.scene.range = self.range*2
                self.range = self.range*2
            elif key == 'a':
                self.scene.forward = self.scene.forward.rotate(angle=0.1, axis=(0,1,0))
            elif key == 'w':
                self.scene.forward = self.scene.forward.rotate(angle=0.1, axis=(0,0,1))
            elif key =='s':
                self.scene.forward = self.scene.forward.rotate(angle=0.1, axis=(1,0,0))

            elif key =='left':
                self.scene.center = self.scene.center+np.array([1,0,0])
            elif key =='right':
                self.scene.center = self.scene.center+np.array([-1,0,0])
            elif key =='up':
                self.scene.center = self.scene.center+np.array([0,1,0])
            elif key =='down':
                self.scene.center = self.scene.center+np.array([0,-1,0])
            else:
                return key
        return None

if __name__ == "__main__":
    win = GUIWindowNew()
    win.functions.append(DrawFunction())
    p = sphere(pos=[1,0,0], radius=1.5, color=color.cyan)
    while 1:
        rate(100)
        win.listen()