from visual import *
from visual.controls import *

from rnamake import structure, util, basic_io
import numpy as np
import gui_window

class VAtom(object):
    def __init__(self, a):
        self.a = a
        self.obj = sphere(pos=a.coords, radius=0.7, color=color.red)

class VResidue(object):
    def __init__(self, res, view_mode=0):
        pass


scene = display(title='RNAMake GUI',
     x=0, y=0, width=800, height=800,
     center=(5,0,0), background=(1,1,1), ambient=color.gray(0.5))

"""c = controls(x=0, y=0, width=250, height=250, range=60)
m1 = menu(pos=(0,0,0), height=7, width=25, text='Options')
bl = button(pos=(-30,30), height=30, width=40, text='Mode', action=lambda: change())
m1.items.append(('Mode', lambda: change())) # specify menu item title and action to perform"""

atoms = []
s = structure.structure_from_pdb("nodes.0.pdb")
atoms.extend(s.atoms())
s = structure.structure_from_pdb("nodes.1.pdb")
atoms.extend(s.atoms())

v_atoms = []
center = util.center(atoms)
for a in atoms:
    v_atoms.append(VAtom(a))



scene.center = center
scene.range = np.array([20,20,20])
range = np.array([20,20,20])

points = []
lines = []
pick = None
dragpos = []


while 1:
    rate(100)
    if scene.kb.keys: # event waiting to be processed?
        key = scene.kb.getkey() # get keyboard info
        if key == 'z':
            scene.range = range/2
            range = range/2
        if key == 'x':
            scene.range = range*2
            range = range*2
        if key == 'a':
            scene.forward = scene.forward.rotate(angle=0.1, axis=(0,1,0))
        if key == 'w':
            scene.forward = scene.forward.rotate(angle=0.1, axis=(0,0,1))
        if key =='s':
            scene.forward = scene.forward.rotate(angle=0.1, axis=(1,0,0))

        if key =='left':
            scene.center = scene.center+np.array([1,0,0])
        if key =='right':
            scene.center = scene.center+np.array([-1,0,0])
        if key =='up':
            scene.center = scene.center+np.array([0,1,0])
        if key =='down':
            scene.center = scene.center+np.array([0,-1,0])
        if key == 'd':
            if len(points) != 0:
                last = points.pop()
                last.visible = False
                del last
            if len(lines) != 0:
                last_l = lines.pop()
                last_l.visible = False
                del last_l



    if scene.mouse.events:
        m1 = scene.mouse.getevent() # get event

        if m1.pick is None:
            p = sphere(pos=m1.pos, radius=1.5, color=color.cyan)
            points.append(p)

            reg_points = []
            for p in points:
                reg_points.append(p.pos)
            f = open("points.pdb", "w")

            str = basic_io.points_to_pdb_str(reg_points)
            f.write(str)
            f.close()

            if len(points) > 1:
                line = cylinder(pos=points[-2].pos, axis=p.pos - points[-2].pos,
                                color=color.black)
                lines.append(line)

        elif m1.pick in points and m1.drag:
                drag_pos = m1.pickpos
                pick = m1.pick

        elif m1.drop:
            pick = None

            for i, l in enumerate(lines):
                l.pos = points[i].pos
                l.axis = points[i+1].pos - points[i].pos

    if pick:
        new_pos = scene.mouse.pos
        if new_pos != drag_pos: # if mouse has moved
            # offset for where the ball was clicked:
            pick.pos += new_pos - drag_pos
            drag_pos = new_pos # update drag position


