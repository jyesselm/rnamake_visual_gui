import argparse

import gui_window_new
import visual_structure
from visual import *

from rnamake import motif_factory, util, basic_io, motif_graph
from rnamake.unittests import build
from rnamake import resource_manager as rm

rm.manager.add_motif("resources/GAAA_tetraloop")

def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-preset',  help='build preset',
                                    required=False)
    parser.add_argument('-mg', help='load mg',
                               required=False)
    parser.add_argument('-s', help='load from save file',
                              required=False)

    args = parser.parse_args()
    return args

def parse_presets(preset_name):
    vmg = visual_structure.VMotifGraph(view_mode=2)
    if preset_name == "ttr":
        m = rm.manager.get_motif(name="GAAA_tetraloop", end_name="A229-A245")
        vmg.add_motif(m)

    return vmg

if __name__ == '__main__':
    args = parse_args()

    gui_window = gui_window_new.get_default_window()

    if args.preset:
        vmg = parse_presets(args.preset)
        gui_window.set_vmg(vmg)
    elif args.s:
        gui_window.load_from_save(args.s)
    elif args.mg:
        f = open(args.mg)
        lines = f.readlines()
        f.close()
        vmg = visual_structure.visual_motif_graph_from_topology(lines[0])
        gui_window.set_vmg(vmg)

    gui_window.setup()

    while 1:
        rate(100)
        gui_window.listen()

