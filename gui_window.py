from visual import *
from visual.controls import *
import numpy as np

class GUIWindowFunction(object):
    pass


class DrawFunction(GUIWindowFunction):
    def __init__(self):
        self.activated = 0
        self.points = []
        self.lines = []

    def listen_for_keys(self, scene):
        if scene.kb.keys: # event waiting to be processed?
            if key == 'd':
                if len(points) != 0:
                    last = self.points.pop()
                    last.visible = False
                    del last
                if len(lines) != 0:
                    last_l = self.lines.pop()
                    last_l.visible = False
                    del last_l

    def listen_for_mouse(self, scene):
        pass


#class


class GUIWindow(object):
    def __init__(self):


        self.c = controls(x=500, y=0, width=250, height=250, range=60)
        self.c.visible = True
        bl = button(pos=(-30,30), height=30, width=40, text='Left',
                    action=lambda: self.test())
        m1 = menu(pos=(0,0,0), height=7, width=25, text='Options')

        self.scene = display(title='RNAMake GUI',
         x=800, y=0, width=800, height=800,
        center=(5,0,0), background=(1,1,1), ambient=color.gray(0.5))

        self.pick = 0
        self.dragpos = []

    def listen(self):
        self.listen_for_keys()
        self.listen_for_mouse()

    def test(self):
        print "made it"

    def listen_for_keys(self):
        if self.scene.kb.keys: # event waiting to be processed?
            key = self.scene.kb.getkey() # get keyboard info
            if key == 'z':
                self.scene.range = range/2
                range = range/2
            if key == 'x':
                self.scene.range = range*2
                range = range*2
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


    def listen_for_mouse(self):
        if self.scene.mouse.events:
            m1 = self.scene.mouse.getevent() # get event

            if m1.pick is None:
                p = sphere(pos=m1.pos, radius=1.5, color=color.cyan)
                self.points.append(p)

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

        """if pick:
            new_pos = scene.mouse.pos
            if new_pos != drag_pos: # if mouse has moved
                # offset for where the ball was clicked:
                pick.pos += new_pos - drag_pos
                drag_pos = new_pos # update drag position"""

if __name__ == "__main__":
    #will not show if no object is created!!!
    gui_window = GUIWindow()
    p = sphere(pos=[1,0,0], radius=1.5, color=color.cyan)

    a = convex(color=(0.5,0,0))
    b = convex(color=(0,0.5,0))
    c = convex(color=(0,0,0.5))
    d = convex(color=(0.5,0,0.5))
    e = convex(color=(0.5,0.5,0))
    f = convex(color=(0,0.5,0.5))

    # triangle
    t = arange(0,2*pi,2*pi/3)

    # disk
    for t in arange(0,2*pi,0.1):
        a.append(pos = (cos(t),0,sin(t)))
        a.append(pos = (cos(t),0.2,sin(t)))

    # box
    for i in range(8):
        p = vector((i/4)%2 - 2.5, (i/2)%2 - 0.5, (i)%2 - 0.5)
        b.append(pos=p)
    #while 1:
    #    rate(100)
    #    gui_window.listen()