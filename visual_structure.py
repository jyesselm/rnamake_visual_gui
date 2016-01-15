from visual import *
from visual.controls import *

from rnamake import util

class VAtom(object):
    def __init__(self, a, color):
        self.a = a
        self.color = color

    def draw(self, view_mode=0):
        if view_mode == 0:
            self.obj = sphere(pos=self.a.coords, radius=0.4, color=self.color)
        else:
            pass


class VResidue(object):
    def __init__(self, res, view_mode=0):
        self.res = res
        self.v_atoms = []

        for a in res.atoms:
            if a is None:
                self.v_atoms.append(None)
            else:
                c = color.red
                if a.name[0] == "P":
                    c = color.orange
                if a.name[0] == "C":
                    c = color.gray(0.9)
                if a.name[0] == "N":
                    c = color.blue

                self.v_atoms.append(VAtom(a, c))

        self.view_mode=view_mode

    def draw_bond(self, i, j):
        pos_i = self.v_atoms[i].obj.pos
        pos_j = self.v_atoms[j].obj.pos
        axis = pos_j - pos_i

        b = cylinder(pos=pos_i, axis=axis, radius=0.20)

    def draw_bonds(self):
        self.draw_bond(0, 1)
        self.draw_bond(0, 2)
        self.draw_bond(0, 3)
        self.draw_bond(3, 4)
        self.draw_bond(4, 5)
        self.draw_bond(5, 6)
        self.draw_bond(5, 7)
        self.draw_bond(5, 7)
        self.draw_bond(7, 8)
        self.draw_bond(6, 9)
        self.draw_bond(7, 10)
        self.draw_bond(9, 10)
        self.draw_bond(10, 11)

        if self.res.name == "G":
            self.draw_bond(12, 13)
            self.draw_bond(13, 14)
            self.draw_bond(13, 15)
            self.draw_bond(15, 16)
            self.draw_bond(16, 17)
            self.draw_bond(17, 18)
            self.draw_bond(18, 19)
            self.draw_bond(17, 20)
            self.draw_bond(20, 21)
            self.draw_bond(21, 22)
            self.draw_bond(22, 9)
            self.draw_bond(22, 16)
            self.draw_bond(12, 18)

    def draw(self, view_mode=0):
        for va in self.v_atoms:
            if va is not None:
                va.draw(view_mode)

        if view_mode == 0:
            self.draw_bonds()


class VChain(object):
    def __init__(self, chain):
        self.chain = chain
        self.v_res = []

        for r in self.chain.residues:
            self.v_res.append(VResidue(r))

    def draw(self, view_mode=0):
        for r in self.v_res:
            r.draw(view_mode)


class VStructure(object):
    def __init__(self, struct):
        self.struct = struct
        self.v_chains = []
        for c in self.struct.chains:
            self.v_chains.append(VChain(c))

    def draw(self, view_mode=0):
        for vc in self.v_chains:
            vc.draw(view_mode)

class VBasepair(object):
    def __init__(self, bp):
        self.bp = bp


class VMotif(object):
    def __init__(self, motif):
        self.motif = motif

        self.v_struct = VStructure(self.motif.structure)

    def draw(self, view_mode=0):
        if view_mode == 0:
            self.v_struct.draw(view_mode)
        if view_mode == 1:
            pos_i = self.motif.ends[0].d()
            pos_j = self.motif.ends[1].d()
            axis = pos_j - pos_i

            dist = util.distance(pos_i, pos_j)

            all_pos = []
            for bp in self.motif.basepairs:
                if bp.bp_type == "cW-W":
                    cylinder(pos=bp.d(), axis=bp.r()[2]*3, radius=10.0, color=color.red)

            #b1 = cylinder(pos=pos_i, axis=self.motif.ends[0].r()[2]*dist, radius=8.0)
            #b2 = cylinder(pos=pos_j, axis=-self.motif.ends[1].r()[2]*dist, radius=8.0)

















