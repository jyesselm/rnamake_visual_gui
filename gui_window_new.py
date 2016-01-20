from visual import *
from visual.graph import *
import numpy as np
import wx

import visual_structure
from rnamake import motif, settings, util, basic_io
from rnamake import resource_manager as rm

class GUIWindowFunction(object):

    def listen(self, scene):
        pass


class DrawFunction(GUIWindowFunction):
    def __init__(self):
        self.name = "Draw"
        self.activated = 1
        self.points = []
        self.highlighted_end = None
        self.lines = []

    def listen_for_keys(self, state):
        if state.key == 'd':
            if len(self.points) != 0:
                last = self.points.pop()
                last.visible = False
                del last
            if len(self.lines) != 0:
                last_l = self.lines.pop()
                last_l.visible = False
                del last_l
            if len(self.points) == 0:
                if self.highlighted_end != None:
                    self.highlighted_end.color = color.green
                    self.highlighted_end = None
        if state.key == 'r':
            all_points = []
            reg_points = []
            for p in self.points:
                reg_points.append(np.array(p.pos))

            for i in range(len(reg_points)-1):
                all_points.append(reg_points[i])
                diff = reg_points[i+1] - reg_points[i]
                unit_vector = util.normalize(diff)
                current = reg_points[i] + unit_vector*5.0
                while util.distance(reg_points[i+1], current) > 5.0:
                    all_points.append(current)
                    current = current + unit_vector*5.0

            s = basic_io.points_to_str(all_points)
            f = open("all_points.str", "w")
            f.write(s)
            f.close()
            basic_io.points_to_pdb("all_points.pdb", all_points)

            f = open("mg.top", "w")
            f.write(state.vmg.mg.topology_to_str() + "\n")
            f.close()

            exit()

    def listen_for_mouse(self, state):
        if state.scene.mouse.events:
            m1 = state.scene.mouse.getevent() # get event

            if m1.pick is None:
                p = sphere(pos=m1.pos, radius=1.5, color=color.cyan)
                self.points.append(p)


                if len(self.points) > 1:
                    line = cylinder(pos=self.points[-2].pos,
                                    axis=p.pos - self.points[-2].pos,
                                    color=color.black)
                    self.lines.append(line)

            elif m1.pick in state.motif_ends:
                m1.pick.color = color.magenta
                self.highlighted_end = m1.pick

                if len(self.points) == 0:
                    p = sphere(pos=m1.pick.pos, radius=1.5, color=color.cyan)
                    self.points.append(p)

    def listen(self, state):
        self.listen_for_keys(state)
        self.listen_for_mouse(state)


class GUIWindowState(object):
    def __init__(self):
        self.scene = None
        self.key = None
        self.motif_ends = []
        self.vmg = visual_structure.VMotifGraph(view_mode=1)



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
        self.tc = wx.TextCtrl(self.p, pos=(100,50), value='',
            size=(800,20), style=wx.TE_MULTILINE)
        self.tc.SetInsertionPoint(len(self.tc.GetValue())+1) #
        self.tc.SetFocus()

        d = 20
        self.scene = display(window=self.window, x=10, y=100, width=1000, height=500,
                            center=(5,0,0), background=(1,1,1), ambient=color.gray(0.5))

        self.range = np.array([20,20,20])
        self.functions = []

        self.state = GUIWindowState()
        self.state.scene = self.scene
        self.display_end_labels = 0

    def _parse_commands(self, cmd):
        words = cmd.split()
        cmd_key = words.pop(0)
        if cmd_key == 'build':
            m = rm.manager.get_motif(name=words[0])
            if len(words) == 1:
                if self.display_end_labels:
                     for i, end in enumerate(self.state.vmg.open_ends):
                        end.hide_label()
                self.state.vmg.add_motif(m)
                if self.display_end_labels:
                    for i, end in enumerate(self.state.vmg.open_ends):
                        end.draw_label(i)
                self.state.motif_ends = [x.obj for x in self.state.vmg.open_ends]
            else:
                pass

        if cmd_key == 'show':
            if words[0] == "labels":
                self.display_end_labels = 1
                for i, end in enumerate(self.state.vmg.open_ends):
                    end.draw_label(i)

        if cmd_key == 'hide':
            if words[0] == "labels":
                self.display_end_labels = 0
                for i, end in enumerate(self.state.vmg.open_ends):
                    end.hide_label()

    def listen(self):
        self.state.key = self.listen_for_keys()
        #self.listen_for_mouse()

        val = self.tc.GetValue()
        spl = val.split("\n")

        if len(spl) > 1:
            self._parse_commands(spl[0])
            self.tc.SetValue("")

        for f in self.functions:
            if not f.activated:
                continue
            f.listen(self.state)

    def setup(self):
        if len(self.state.vmg.mg.graph) == 0:
            path = settings.RESOURCES_PATH + "/motifs/base.motif"
            m = motif.file_to_motif(path)
            self.state.vmg.add_motif(m)
            self.state.motif_ends = [x.obj for x in self.state.vmg.open_ends]

    def set_vmg(self, vmg):
        self.state.vmg = vmg
        self.state.motif_ends =  [x.obj for x in vmg.open_ends]

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
            elif key =='e':
                exit()
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

def get_default_window():
    win = GUIWindowNew()
    win.functions.append(DrawFunction())
    return win


if __name__ == "__main__":
    win = GUIWindowNew()
    win.functions.append(DrawFunction())
    win.setup()
    #p = sphere(pos=[1,0,0], radius=1.5, color=color.cyan)
    while 1:
        rate(100)
        win.listen()