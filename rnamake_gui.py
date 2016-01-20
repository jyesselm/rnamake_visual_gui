import argparse

import gui_window_new
import visual_structure
from visual import *

from rnamake import motif_factory, util, basic_io, motif_graph
from rnamake.unittests import build
from rnamake import resource_manager as rm

def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-preset',  help='build preset',
                                    required=False)

    args = parser.parse_args()
    return args

def parse_presets(preset_name):
    vmg = visual_structure.VMotifGraph(view_mode=1)
    if preset_name == "ttr":
        rm.manager.add_motif("resources/GAAA_tetraloop")
        m = rm.manager.get_motif(name="GAAA_tetraloop", end_name="A229-A245")
        vmg.add_motif(m)

    return vmg

if __name__ == '__main__':
    args = parse_args()

    gui_window = gui_window_new.get_default_window()

    if args.preset:
        vmg = parse_presets(args.preset)
        gui_window.set_vmg(vmg)

    gui_window.setup()

    while 1:
        rate(100)
        gui_window.listen()
