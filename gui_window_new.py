from visual import *
from visual.graph import *
import numpy as np
import wx
import copy

import visual_structure
import path_builder
from rnamake import motif, settings, util, basic_io, motif_tree
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
        self.highlighted_ends = []
        self.lines = []
        self.wrapper = wrapper.FollowPathWrapper()
        self.just_built = 0

        self.full_path = []

    def listen_for_keys(self, state):
        if state.key == 'd':
            if len(self.points) != 0:
                last = self.points.pop()
                for h_end in self.highlighted_ends:
                    if h_end.point == last:
                        h_end.end.color = color.green
                        self.highlighted_ends.remove(h_end)
                        break
                last.visible = False
                del last

            if len(self.lines) != 0:
                last_l = self.lines.pop()
                last_l.visible = False
                del last_l

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

            print "all points: ", len(all_points)

            f = open("mg.top", "w")
            f.write(state.vmg.mg.topology_to_str() + "\n")
            actual_open_end = None
            actual_ni = 0
            for end in self.highlighted_ends:
                for ni, open_end in state.vmg.open_bp_ends:
                    if open_end.obj == end.end:
                        actual_open_end = open_end
                        actual_ni = ni
                        f.write(str(ni) + " " + open_end.name() + "\n")
            f.close()

            self.wrapper.run(path="all_points.str", mg="mg.top")

            f = open("mt_out.top")
            lines = f.readlines()
            f.close()

            mt = motif_tree.motif_tree_from_topology_str(lines[0])
            actual_open_end.obj.color = color.red
            state.vmg.mg.increase_level()
            print actual_ni, actual_open_end.name()
            state.vmg.add_motif_tree(mt, actual_ni, actual_open_end.name())
            self.just_built = 1

        if state.key == 'k':
            if self.just_built == 1:
                self.just_built = 0
                self.full_path.extend([ x.pos for x in self.points])
                for p in self.points:
                    p.visible = False
                for l in self.lines:
                    l.visible = False
                self.points = []
                self.lines = []

        if state.key == 'l':
            if self.just_built == 1:
                self.just_built = 0
                state.vmg.remove_node_level()
                state.vmg.mg.decrease_level()

    def listen_for_mouse(self, state):
        if state.scene.mouse.events:
            m1 = state.scene.mouse.getevent() # get event

            if m1.pick is None:
                p = sphere(pos=m1.pos, radius=1.5, color=color.cyan)
                self.points.append(p)


                if len(self.points) > 1:
                    line = cylinder(pos=self.points[-2].pos,
                                    axis=p.pos - self.points[-2].pos,
                                    color=color.black,
                                    radius = 8.0)
                    self.lines.append(line)

            elif m1.pick in state.vmg.open_ends:
                for h_end in self.highlighted_ends:
                    if m1.pick == h_end.end:
                        return

                m1.pick.color = color.magenta
                p = sphere(pos=m1.pick.pos, radius=1.5, color=color.cyan)
                self.highlighted_ends.append(HighlightedEnd(m1.pick, p))
                self.points.append(p)

                if len(self.points) > 1:
                    line = cylinder(pos=self.points[-2].pos,
                                    axis=p.pos - self.points[-2].pos,
                                    color=color.black)
                    self.lines.append(line)



    def listen(self, state):
        self.listen_for_keys(state)
        self.listen_for_mouse(state)


class DrawFunctionNew(GUIWindowFunction):
    def __init__(self):
        self.name = "Draw"
        self.activated = 1
        self.curve = curve(radius=8)
        self.points = []
        self.highlighted_end = None
        self.highlighted_ends = []
        self.lines = []
        self.wrapper = wrapper.FollowPathWrapper()
        self.just_built = 0

        self.full_path = []

    def listen_for_keys(self, state):
        if state.key == 'd':
            self.curve.visible = False
            del self.curve

            if len(self.points) > 0:
                self.points.pop()
                self.curve = curve(pos=self.points, radius=8, color=color.cyan)

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

            print "all points: ", len(all_points)

            f = open("mg.top", "w")
            f.write(state.vmg.mg.topology_to_str() + "\n")
            actual_open_end = None
            actual_ni = 0
            for end in self.highlighted_ends:
                for ni, open_end in state.vmg.open_bp_ends:
                    if open_end.obj == end.end:
                        actual_open_end = open_end
                        actual_ni = ni
                        f.write(str(ni) + " " + open_end.name() + "\n")
            f.close()

            self.wrapper.run(path="all_points.str", mg="mg.top")

            f = open("mt_out.top")
            lines = f.readlines()
            f.close()

            mt = motif_tree.motif_tree_from_topology_str(lines[0])
            actual_open_end.obj.color = color.red
            state.vmg.mg.increase_level()
            print actual_ni, actual_open_end.name()
            state.vmg.add_motif_tree(mt, actual_ni, actual_open_end.name())
            self.just_built = 1

        if state.key == 'k':
            if self.just_built == 1:
                self.just_built = 0
                self.full_path.extend([ x.pos for x in self.points])
                for p in self.points:
                    p.visible = False
                for l in self.lines:
                    l.visible = False
                self.points = []
                self.lines = []

        if state.key == 'l':
            if self.just_built == 1:
                self.just_built = 0
                state.vmg.remove_node_level()
                state.vmg.mg.decrease_level()

    def listen_for_mouse(self, state):
        if state.scene.mouse.events:
            m1 = state.scene.mouse.getevent() # get event

            if m1.pick is None:

                if len(self.points) > 1:
                    dist = util.distance(self.points[-1], m1.pos)
                    if dist < 1:
                        return

                self.points.append(m1.pos)
                self.curve.append(pos=m1.pos, color=color.cyan)

            elif m1.pick in state.vmg.open_ends:
                pass
                """for h_end in self.highlighted_ends:
                    if m1.pick == h_end.end:
                        return

                m1.pick.color = color.magenta
                p = sphere(pos=m1.pick.pos, radius=1.5, color=color.cyan)
                self.highlighted_ends.append(HighlightedEnd(m1.pick, p))
                self.points.append(p)

                if len(self.points) > 1:
                    line = cylinder(pos=self.points[-2].pos,
                                    axis=p.pos - self.points[-2].pos,
                                    color=color.black)
                    self.lines.append(line)"""



    def listen(self, state):
        self.listen_for_keys(state)
        self.listen_for_mouse(state)


class DrawFunctionNew2(GUIWindowFunction):
    def __init__(self):
        self.name = "Draw"
        self.activated = 1
        self.points = []
        self.highlighted_ends = []
        self.lines = []
        self.built = 0
        self.path_builder = path_builder.PathBuilder()

        self.full_path = []
        self.pick = None
        self.dragpos = [0,0,0]
        self.count = 0

        self.previous_points = []


    def listen_for_keys(self, state):
        if state.key == 'u':
            if len(self.previous_points) > 0:
                pos = self.previous_points.pop()
                for i, p in enumerate(self.points):
                    p.pos = pos[i]
                self._update_path()

        if state.key == 'd':
            if len(self.points) == 0:
                return

            last = self.points.pop()
            last.visible = False
            del last

            if len(self.lines) != 0:
                last_l = self.lines.pop()
                last_l.visible = False
                del last_l

                if len(self.lines) != 0:
                    last_l = self.lines.pop()
                    last_l.visible = False
                    del last_l

            if len(self.points) == 1:
                last  = self.points.pop()
                last.visible = False
                del last


        if state.key == 'r':
            self._run_path_finding(state)

    def _add_points_on_rna(self, m1, state):
        for ni, v_end in state.vmg.open_bp_ends:
            if not v_end.clicked(m1.pick):
                continue

            self.highlighted_ends.append([ni, v_end])

            if len(self.points) > 1:
                return

            pos = v_end.d
            if len(self.points) > 0:
                dist = util.distance(pos, self.points[-1].pos)
                if dist < 1:
                    return

            p = sphere(pos=pos, radius=0.1, color=color.cyan)
            self.points.append(p)

            dir = v_end.r[2]
            line = cylinder(pos=pos, axis=-dir*20,
                            color=color.cyan, radius=7)

            self.lines.append(line)

            new_pos = pos - dir*20
            p = sphere(pos=new_pos, radius=7.5, color=color.cyan)
            self.points.append(p)

    def _run_path_finding(self, state):
        if self.built:
            state.vmg.remove_node_level()
            state.vmg.mg.decrease_level()

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
        f.write(str(self.highlighted_ends[0][0]) + " " + self.highlighted_ends[0][1].name())
        f.close()

        self.path_builder.build()

        f = open("mt_out.top")
        lines = f.readlines()
        f.close()

        mt = motif_tree.motif_tree_from_topology_str(lines[0])
        state.vmg.mg.increase_level()
        state.vmg.add_motif_tree(mt,
                                 self.highlighted_ends[0][0],
                                 self.highlighted_ends[0][1].name())

        for p in self.points:
            p.opacity = 0.5
        for l in self.lines:
            l.opacity = 0.5

        self.built = 1

    def _update_path(self):
        count = 1
        for i, l in enumerate(self.lines):
            if i == 0:
                l.pos = self.points[i].pos
                l.axis = self.points[i+1].pos - self.points[i].pos
            else:
                if i % 2 == 1:
                    l.pos = self.points[count].pos
                    l.axis = (self.points[count+1].pos - self.points[count].pos)/2
                else:
                    new_pos = self.points[count].pos + \
                              (self.points[count+1].pos - self.points[count].pos)/2
                    l.pos = new_pos
                    l.axis = (new_pos - self.points[count].pos)
                    count +=1

    def listen_for_mouse(self, state):
        if  state.m_event:
            m1 = state.m_event# get event

            if m1.drop:
                self.pick = None
                self._update_path()

            if m1.button == 'left' and m1.alt and m1.pick:
                if m1.pick in self.points and m1.drag:
                    dist = util.distance(self.dragpos, m1.pickpos)
                    if dist < 1:
                        return

                    self.previous_points.append([vector(p.pos) for p in self.points])

                    self.dragpos = m1.pickpos
                    self.pick = m1.pick

                else:
                    self._add_points_on_rna(m1, state)

            elif m1.button == 'left' and m1.alt and not m1.drag:

                pos = m1.pos
                if len(self.points) > 0:
                    dist = util.distance(pos, self.points[-1].pos)
                    if dist < 1:
                        return

                #need points on RNA first
                if len(self.points) == 0:
                    return

                p = sphere(pos=pos, radius=7.5, color=color.cyan)
                self.points.append(p)


                if len(self.points) > 1:
                    line = cylinder(pos=self.points[-2].pos,
                                    axis=(p.pos - self.points[-2].pos)/2,
                                    color=color.cyan,
                                    radius = 7)
                    self.lines.append(line)

                    new_pos = self.points[-2].pos + (p.pos - self.points[-2].pos)/2
                    line = cylinder(pos=new_pos,
                                    axis=(new_pos - self.points[-2].pos),
                                    color=color.cyan,
                                    radius = 7)
                    self.lines.append(line)


    def listen(self, state):
        self.listen_for_keys(state)
        self.listen_for_mouse(state)

        if self.pick:
            new_pos = state.scene.mouse.pos
            if new_pos != self.dragpos:
                self.pick.pos += new_pos - self.dragpos
                self.dragpos = new_pos


class GUIWindowState(object):
    def __init__(self):
        self.scene = None
        self.key = None
        self.vmg = visual_structure.VMotifGraph(view_mode=2)


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
                            center=(5,0,0), background=(1,1,1), ambient=color.gray(0.5),
                            userspin=False, userzoom=False)

        self.range = np.array([20,20,20])
        self.scene.range = self.range
        self.functions = []

        self.state = GUIWindowState()
        self.state.scene = self.scene
        self.display_end_labels = 0
        self.lastpos = self.scene.center

        self.dragging = 0
        self.zooming = 0

    def _parse_commands(self, cmd):
        words = cmd.split()
        cmd_key = words.pop(0)
        if cmd_key == 'build':
            m = rm.manager.get_motif(name=words[0].upper())
            if len(words) == 1:
                if self.display_end_labels:
                     for i, end in enumerate(self.state.vmg.open_ends):
                        end.hide_label()
                self.state.vmg.add_motif(m)
                if self.display_end_labels:
                    for i, end in enumerate(self.state.vmg.open_ends):
                        end.draw_label(i)
            else:
                if words[1] == "on":
                    num = int(words[2])
                    ni, end = self.state.vmg.open_bp_ends[num]
                    self.state.vmg.add_motif(m, parent_index=ni,
                                             parent_end_name=end.name())


        if cmd_key == 'show':
            if words[0] == "labels":
                j = 0
                self.display_end_labels = 1

                for i, end in self.state.vmg.open_bp_ends:
                    end.draw_label(j)
                    j += 1

        if cmd_key == 'hide':
            if words[0] == "labels":
                self.display_end_labels = 0
                for i, end in enumerate(self.state.vmg.open_ends):
                    end.hide_label()

        if cmd_key == 'save':
            if len(words) > 0:
                f = open(words[0] + ".top", "w")
                f.write(self.state.vmg.mg.topology_to_str())
                f.close()
            else:
                f = open("save.top", "w")
                f.write(self.state.vmg.mg.topology_to_str())
                f.close()

    def listen(self):
        self.state.key = self.listen_for_keys()
        self.state.m_event = self.listen_for_mouse()

        if self.dragging:
            vec1 = util.normalize(self.scene.mouse.pos - self.lastpos)

            if util.distance(vec1, [0, 0, 0]) > 0.1:
                vec2 = self.scene.forward
                rotation = cross(vec1, vec2)
                mag = util.distance(self.scene.mouse.pos - self.lastpos, [0,0,0])
                self.scene.forward = self.scene.forward.rotate(angle=0.0007*mag,
                                                               axis=rotation)

                if self.scene.forward.y > 0.90:
                    self.scene.forward.y = 0.90
                if self.scene.forward.y < -0.90:
                    self.scene.forward.y = -0.90

        if self.zooming:
            vec1 = util.normalize(self.scene.mouse.pos - self.lastpos)

            if util.distance(vec1, [0, 0, 0]) > 0.1:

                mag = util.distance(self.scene.mouse.pos - self.lastpos, [0,0,0])
                if vec1[1] > 0:
                    self.scene.range = self.range/(1.000 + 0.0005*mag)
                    self.range = self.range/(1.000 + 0.0005*mag)
                if vec1[1] < 0:
                    self.scene.range = self.range/(1.000 - 0.0005*mag)
                    self.range = self.range/(1.000 - 0.0005*mag)


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


    def set_vmg(self, vmg):
        self.state.vmg = vmg

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

    def listen_for_mouse(self):
        if self.scene.mouse.events:
            m1 = self.scene.mouse.getevent() # get event

            if m1.button == 'left' and m1.drag and not m1.alt:
                self.lastpos = m1.pos
                self.dragging = 1

            if  m1.button == 'left' and m1.drop and not m1.alt:
                self.dragging = 0

            if m1.button == 'right' and m1.drag and not m1.alt:
                self.lastpos = m1.pos
                self.zooming = 1

            if m1.button == 'right' and m1.drop and not m1.alt:
                self.zooming = 0

            return m1

        return None








def get_default_window():
    win = GUIWindowNew()
    win.functions.append(DrawFunctionNew2())
    return win


if __name__ == "__main__":
    win = GUIWindowNew()
    win.functions.append(DrawFunction())
    win.setup()

    while 1:
        rate(100)
        win.listen()