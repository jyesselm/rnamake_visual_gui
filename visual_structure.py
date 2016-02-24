from visual import *
from visual.controls import *
import numpy as np

from rnamake import util, motif_graph, motif_type, atom, primitives, motif_factory, residue
from rnamake import resource_manager as rm

class Drawable(object):
    def __init__(self):
        self.view_mode = 0
        self.drawn = 0

    def draw(self, view_mode=0):
        raise RuntimeError("tried to call abstract method Drawable:draw")

    def clear(self):
        raise RuntimeError("tried to call abstract method Drawable:clear")


class VAtom(atom.Atom, Drawable):
    def __init__(self, a, color):
        atom.Atom.__init__(self, a.name, a.coords)
        Drawable.__init__(self)
        self.color = color

    def draw(self, view_mode=0):
        self.view_mode = view_mode
        if view_mode == 0:
            self.obj = sphere(pos=self.coords, radius=0.4, color=self.color)
            self.drawn = 1

    def clear(self):
        if not self.drawn:
            return
        if self.view_mode == 0:
            self.obj.visible = False
            del self.obj
            self.obj = None
            self.drawn = 0


class VResidue(primitives.Residue, Drawable):
    def __init__(self, res):
        primitives.Residue.__init__(self, res.name, res.num, res.chain_id, res.i_code)
        Drawable.__init__(self)
        self.rtype = res.rtype
        self.uuid = res.uuid
        self.atoms = []
        self.view_mode = 0
        self.drawn = 0
        self.bonds = []
        self.cartoon_color = color.yellow
        self.cartoons = []
        self.rod = None

        for a in res.atoms:
            if a is None:
                self.atoms.append(None)
            else:
                c = color.red
                if a.name[0] == "P":
                    c = color.orange
                if a.name[0] == "C":
                    c = color.gray(0.9)
                if a.name[0] == "N":
                    c = color.blue

                self.atoms.append(VAtom(a, c))

    def get_beads(self):
        """
		Generates steric beads required for checking for steric clashes between
		motifs. Each residues has three beads modeled after the typical three
		bead models used in coarse grain modeling. The three beads are,
		Phosphate (P, OP1, OP2) Sugar (O5',C5',C4',O4',C3',O3',C1',C2',O2')
		and Base (All remaining atoms).
		"""
        phos_atoms,sugar_atoms,base_atoms = [],[],[]

        for i,a in enumerate(self.atoms):
            if a is None:
                continue
            if   i < 3:
                phos_atoms.append(a)
            elif i < 12:
                sugar_atoms.append(a)
            else:
                base_atoms.append(a)

        beads = []
        types = [residue.BeadType.PHOS, residue.BeadType.SUGAR, residue.BeadType.BASE]
        for i,alist in enumerate([phos_atoms,sugar_atoms,base_atoms]):
            if len(alist) > 0:
                beads.append(residue.Bead(util.center(alist), types[i]))

        return beads

    def draw_bond(self, i, j):
        pos_i = self.atoms[i].coords
        pos_j = self.atoms[j].coords
        axis = pos_j - pos_i

        b = cylinder(pos=pos_i, axis=axis, radius=0.20, color=self.cartoon_color)
        self.bonds.append(b)

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

        if self.name == "G":
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

    def draw_cartoon(self, points, norm):
        cartoon = convex(color=self.cartoon_color)
        for p in points:
            cartoon.append(pos = p-norm)
            cartoon.append(pos = p+norm)

        return cartoon

    def draw_base_cartoon(self, indices, pos1, pos2):
        points = []
        for i in indices:
            points.append(self.atoms[i].coords)


        dir1 = points[0] - points[pos1]
        dir2 = points[0] - points[pos2]
        norm = util.normalize(np.cross(dir1, dir2))*0.25

        self.cartoons.append(self.draw_cartoon(points, norm))

    def draw(self, view_mode=0):
        self.view_mode = view_mode
        self.drawn = 1
        for va in self.atoms:
            if va is not None:
                va.draw(view_mode)

        if view_mode == 0:
            self.draw_bonds()

        if view_mode == 1:
            beads = self.get_beads()
            pos_i = beads[1].center
            pos_j = beads[2].center
            axis = pos_j - pos_i
            self.rod = cylinder(pos=pos_i, axis=axis, radius=1.0,
                                color=color.blue)

        if view_mode == 2:
            sugar_points = []
            sugar_points.append( self.atoms[5].coords)
            sugar_points.append( self.atoms[6].coords)
            sugar_points.append( self.atoms[9].coords)
            sugar_points.append( self.atoms[10].coords)
            sugar_points.append( self.atoms[7].coords)

            dir1 = self.atoms[5].coords - self.atoms[9].coords
            dir2 = self.atoms[5].coords - self.atoms[10].coords
            norm = util.normalize(np.cross(dir1, dir2))*0.25
            if len(self.cartoons) > 0:
                return

            self.cartoons = [ self.draw_cartoon(sugar_points, norm) ]

            if self.rtype.name == "ADE":
                self.draw_base_cartoon([21, 20, 19, 16, 15], 3, 2)
                self.draw_base_cartoon([17, 16, 15, 14, 13, 12], 3, 2)
                self.draw_bond(21, 9)

            elif self.rtype.name == "GUA":
                self.draw_base_cartoon([22, 21, 20, 17, 16], 3, 2)
                self.draw_base_cartoon([17, 16, 18, 12, 13, 15], 3, 2)
                self.draw_bond(22, 9)

            else:
                self.draw_base_cartoon([12, 13, 15, 16, 18, 19], 3, 2)
                self.draw_bond(12, 9)

    def clear(self):
        if self.drawn == 0:
            return
        #self.drawn = 0

        if self.view_mode == 0:
            for a in self.atoms:
                a.clear()

            for b in self.bonds:
                b.visible = False
                del b
            self.bonds = []

        if self.view_mode == 1:
            self.rod.visible = False
            del self.rod
            self.rod = None

        while len(self.cartoons) > 0:
            c = self.cartoons.pop()
            c.visible = False
            del c

        while len(self.bonds) > 0:
            b = self.bonds.pop()
            b.visible = False
            del b


class VBasepair(primitives.Basepair, Drawable):
    def __init__(self, res1, res2, bp):
        primitives.Basepair.__init__(self, res1, res2, bp.bp_type)
        Drawable.__init__(self)
        self.obj = None
        self.label = None
        self.r = bp.r()
        self.d = bp.d()

    def _get_atoms(self):
        atoms = []
        for a in self.res1.atoms:
            if a is not None:
                atoms.append(a)
        for a in self.res2.atoms:
            if a is not None:
                atoms.append(a)
        return atoms

    def d(self):
        atoms = self._get_atoms()
        return util.center(atoms)

    def draw(self, view_mode=0):
        self.view_mode = view_mode
        self.drawn = 1
        if view_mode == 1 and self.bp_type == "cW-W":
            self.obj = cylinder(pos=self.d(), axis=self.r[2]*3,
                                  radius=8.0, color=color.red)

    def draw_label(self, num):
        self.label = label(pos=self.obj.pos, text='End: ' + str(num),
                           space=self.obj.radius, color=color.black)

    def hide_label(self):
        self.label.visible = False
        del self.label
        self.label = None

    def clear(self):
        if self.drawn == 0:
            return
        self.drawn = 0
        if self.view_mode == 1:
            self.obj.visible = False
            del self.obj
            self.obj = None
        if self.view_mode == 2:
            self.res1.clear()
            self.res2.clear()

    def highlight(self):
        if self.view_mode == 2:
            for c in self.res1.cartoons:
                c.color = color.magenta
            self.res1.bonds[0].color = color.magenta
            for c in self.res2.cartoons:
                c.color = color.magenta
            self.res2.bonds[0].color = color.magenta

    def clicked(self, obj):
        if self.view_mode == 2:
            for c in self.res1.cartoons:
                if c == obj:
                    return 1
            for c in self.res2.cartoons:
                if c == obj:
                    return 1
        return 0


class VChain(primitives.Chain, Drawable):
    def __init__(self, chain):
        residues = []
        for r in chain.residues:
            residues.append(VResidue(r))
            if r.rtype.name == "ADE":
                residues[-1].cartoon_color = color.yellow
            elif r.rtype.name == "GUA":
                residues[-1].cartoon_color = color.red
            elif r.rtype.name == "URA":
                residues[-1].cartoon_color = color.blue
            elif r.rtype.name == "CYT":
                residues[-1].cartoon_color = color.green

        primitives.Chain.__init__(self, residues)
        Drawable.__init__(self)
        self.obj = None

    def draw(self, view_mode=0):
        self.view_mode = view_mode
        self.drawn = 1
        for r in self.residues:
            r.draw(view_mode)

        if view_mode == 2:
            points = []
            for r in self.residues:
                atoms = []
                for i in (0,1,2,3,4,5):
                    if r.atoms[i] is not None:
                        atoms.append(r.atoms[i])
                center = util.center(atoms)
                points.append(center)
            self.obj = curve(radius=0.5, color=color.orange)
            for p in points:
                self.obj.append(pos=p)

    def clear(self):
        if self.drawn == 0:
            return
        self.drawn = 0
        for r in self.residues:
            r.clear()
        if self.view_mode == 2:
            self.obj.visible = False
            del self.obj


class VStructure(primitives.Structure, Drawable):
    def __init__(self, struct):
        chains = []
        for c in struct.chains:
            chains.append(VChain(c))
        primitives.Structure.__init__(self, chains)
        Drawable.__init__(self)

    def draw(self, view_mode=0):
        self.drawn = 1
        for vc in self.chains:
            vc.draw(view_mode)

    def clear(self):
        if self.drawn == 0:
            return
        self.drawn = 0
        for vc in self.chains:
            vc.clear()


class VMotif(primitives.Motif, Drawable):
    def __init__(self, motif):
        struct = VStructure(motif.structure)
        self.mtype = motif.mtype
        self.id = motif.id
        basepairs = []
        ends = []

        for bp in motif.basepairs:
            res1 = struct.get_residue(uuid=bp.res1.uuid)
            res2 = struct.get_residue(uuid=bp.res2.uuid)
            basepairs.append(VBasepair(res1, res2, bp))

        for end in motif.ends:
            i = motif.basepairs.index(end)
            ends.append(basepairs[i])

        primitives.Motif.__init__(self, struct, basepairs, ends)
        Drawable.__init__(self)

    def _draw_cartoon(self, view_mode):
        for bp in self.basepairs:
            bp.draw(view_mode)

        if self.mtype == motif_type.HELIX:
            return

        end_res = []
        for end in self.ends:
            end_res.extend(end.residues())

        for r in self.structure.residues():
            if r in end_res:
                continue
            r.draw(view_mode)

    def draw(self, view_mode=0):
        if self.drawn == 1 and self.view_mode == view_mode:
            return

        self.drawn = 1
        self.view_mode = view_mode

        for bp in self.basepairs:
            bp.draw(view_mode)

        if view_mode == 0:
            self.structure.draw(view_mode)

        if view_mode == 1:
            self._draw_cartoon(view_mode)

        if view_mode == 2:
            self.structure.draw(view_mode)
            self._draw_cartoon(view_mode)

    def clear(self):
        if self.drawn == 0:
            return

        self.drawn = 0
        if self.view_mode == 0:
            self.structure.clear()

        if self.view_mode == 1:
            for bp in self.basepairs:
                bp.clear()
            for r in self.structure.residues():
                r.clear()

        if self.view_mode == 2:
            self.structure.clear()
            for bp in self.basepairs:
                bp.clear()
            for r in self.structure.residues():
                r.clear()


class VMotifGraph(object):
    def __init__(self, mg=None, view_mode=0):
        self.mg = None
        self.v_motifs = {}
        self.open_ends = []
        self.view_mode = view_mode
        if mg is None:
            self.mg = motif_graph.MotifGraph()
            self.mg.option('sterics', 0)
        else:
            self.mg = mg
            for n in self.mg.graph:
                self.v_motifs.append(VMotif(n.data))

    def add_motif_tree(self, mt, parent_index, parent_end_name):

        last_pos = self.mg.last_node().index
        self.mg.add_motif_tree(mt, parent_index, parent_end_name)

        for n in self.mg.graph:
            if n.index > last_pos:
                self.v_motifs[n.index] = VMotif(n.data)

        self.draw(self.view_mode)

        for n in self.mg.graph:
             if n.index > last_pos:
                self.v_motifs[n.index].ends[0].clear()


    def add_motif(self, m=None, parent_index=-1, parent_end_index=-1,
                  parent_end_name=None, m_name=None, m_end_name=None):

        pos = self.mg.add_motif(m, parent_index, parent_end_index,
                                parent_end_name, m_name, m_end_name)

        if pos == -1:
            return pos

        new_m = self.mg.last_node().data

        self.v_motifs[pos] = VMotif(new_m)
        self.v_motifs[pos].ends[0].clear()
        self.draw(self.view_mode)

    def remove_node_level(self, level=None):
        self.mg.remove_node_level(level)

        remove = []
        for i, v_m in self.v_motifs.iteritems():
            try:
                n = self.mg.get_node(i)
            except:
                remove.append(i)

        for r in remove:
            v_m = self.v_motifs[r]
            v_m.clear()
            del self.v_motifs[r]

        self.highlight_open_ends()

    def draw(self, view_mode=0):
        for v_m in self.v_motifs.values():
            v_m.draw(view_mode)

        self.highlight_open_ends()

    def highlight_open_ends(self):
        leaf_and_ends = self.mg.leafs_and_ends()
        self.open_bp_ends = []
        for n, i in leaf_and_ends:
            ni = n.index
            v_end = self.v_motifs[ni].ends[i]
            self.open_bp_ends.append([ni, v_end])

        for ni, v_end in self.open_bp_ends:
            v_end.highlight()


def visual_motif_graph_from_topology(s):
    spl = s.split("&")
    node_spl = spl[0].split("|")
    vmg = VMotifGraph(view_mode=1)
    for i, n_spl in enumerate(node_spl[:-1]):
        sspl = n_spl.split(",")
        if rm.manager.motif_exists(name=sspl[0], end_name=sspl[1], end_id=sspl[2]):
            m = rm.manager.get_motif(name=sspl[0], end_name=sspl[1], end_id=sspl[2])
        elif rm.manager.motif_exists(name=sspl[0], end_id=sspl[2]):
            m = rm.manager.get_motif(name=sspl[0], end_id=sspl[2])
            print "warning: cannot find exact motif"
        else:
            print sspl
            raise ValueError("cannot find motif")

        pos = vmg.add_motif(m, parent_index=int(sspl[3]), parent_end_name=sspl[4])
        #print pos, sspl
        if pos == -1:
            raise ValueError("cannot get mg from topology failed to add motif")

    if len(spl) == 1:
        return vmg
    connection_spl = spl[1].split("|")
    for c_spl in connection_spl[:-1]:
        sspl = c_spl.split()
        vmg.add_connection(int(sspl[0]), int(sspl[1]), sspl[2], sspl[3])

    return vmg



if __name__ == "__main__":
    rm.manager.add_motif("resources/GAAA_tetraloop")
    m = rm.manager.get_motif(name="GAAA_tetraloop", end_name="A229-A245")
    vmg = VMotifGraph(view_mode=2)
    vmg.add_motif(m)
    #for i, end in enumerate(vmg.open_ends):
    #    end.draw_label(i)





