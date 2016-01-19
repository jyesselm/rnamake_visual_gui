import argparse

import gui_window_new
import visual_structure
from visual import *

from rnamake import motif_factory, util, basic_io
from rnamake.unittests import build


gui_window = gui_window_new.GUIWindowNew()
gui_window.setup()

builder = build.BuildMotifGraph()
mg = builder.build(10)
vmg = visual_structure.VMotifGraph(mg)
vmg.draw(1)

while 1:
    rate(100)
    gui_window.listen()

"""m0 = motif_factory.factory.motif_from_file("nodes.0.pdb")
m1 = motif_factory.factory.motif_from_file("nodes.1.pdb")
vm0 = visual_structure.VMotif(m0)
vm1 = visual_structure.VMotif(m1)

vm0.draw(view_mode=0)
#vm1.draw(view_mode=0)
vm1.draw(view_mode=1)"""