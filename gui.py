import gui_window_new
import visual_structure

from rnamake import motif_factory, util, basic_io


gui_window = gui_window_new.GUIWindowNew()

m = motif_factory.factory.motif_from_file("nodes.0.pdb")
vm = visual_structure.get_visual_motif(m)
