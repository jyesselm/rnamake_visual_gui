from visual import *
from visual.controls import *

from rnamake import util, motif_graph, motif_type, atom, primitives, motif_factory, residue

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
        pos_i = self.atoms[i].obj.pos
        pos_j = self.atoms[j].obj.pos
        axis = pos_j - pos_i

        b = cylinder(pos=pos_i, axis=axis, radius=0.20)
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

    def clear(self):
        if self.drawn == 0:
            return
        self.drawn = 0

        for a in self.atoms:
            a.clear()

        if self.view_mode == 0:
            for b in self.bonds:
                b.visible = False
                del b
            self.bonds = []

        if self.view_mode == 1:
            self.rod.visible = False
            del self.rod
            self.rod = None


class VBasepair(primitives.Basepair, Drawable):
    def __init__(self, res1, res2, bp):
        primitives.Basepair.__init__(self, res1, res2, bp.bp_type)
        Drawable.__init__(self)
        self.obj = None
        self.r = bp.r()

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
        if view_mode == 1:
            self.drawn = 1
            self.obj = cylinder(pos=self.d(), axis=self.r[2]*3,
                                  radius=8.0, color=color.red)

    def clear(self):
        if self.drawn == 0:
            return
        self.drawn = 0
        if self.view_mode == 1:
            self.obj.visible = False
            del self.obj
            self.obj = None


class VChain(primitives.Chain, Drawable):
    def __init__(self, chain):
        residues = []
        for r in chain.residues:
            residues.append(VResidue(r))

        primitives.Chain.__init__(self, residues)
        Drawable.__init__(self)

    def draw(self, view_mode=0):
        self.drawn = 1
        for r in self.residues:
            r.draw(view_mode)

    def clear(self):
        if self.drawn == 0:
            return
        self.drawn = 0
        for r in self.residues:
            r.clear()


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
            if bp.bp_type == "cW-W":
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
        self.drawn = 1
        self.view_mode = view_mode

        if view_mode == 0:
            self.structure.draw(view_mode)

        if view_mode == 1:
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
            for r in self.structure.residues:
                r.clear()

class VMotifGraph(object):
    def __init__(self, mg=None):
        self.mg = None
        self.v_motifs = []
        self.open_ends = []
        if mg is None:
            self.mg = motif_graph.MotifGraph()
        else:
            self.mg = mg
            for n in self.mg.graph:
                self.v_motifs.append(VMotif(n.data))


    def add_motif(self, m=None, parent_index=-1, parent_end_index=-1,
                  parent_end_name=None, m_name=None, m_end_name=None):

        pos = self.mg.add_motif(m, parent_index, parent_end_index,
                                parent_end_name, m_name, m_end_name)

        if pos == -1:
            return pos

        new_m = self.mg.last_node().data

        self.v_motifs.append(VMotif(new_m))
        self.draw(1)

    def draw(self, view_mode=0):
        for v_m in self.v_motifs:
            v_m.draw(view_mode)

        self.open_ends = []
        leaf_and_ends = self.mg.leafs_and_ends()
        for n, i in leaf_and_ends:
            ni = n.index
            v_end = self.v_motifs[ni].v_ends[i]
            self.open_ends.append(v_end)

        for v_end in self.open_ends:
            v_end.color = color.green

        for v_m in self.v_motifs:
            for end in v_m.v_ends:
                if end not in self.open_ends:
                    end.color = color.red


if __name__ == "__main__":
    m0 = motif_factory.factory.motif_from_file("nodes.0.pdb")
    vm = VMotif(m0)
    vm.draw(1)











