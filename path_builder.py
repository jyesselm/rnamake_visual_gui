from rnamake import basic_io, util, motif_tree, motif_graph, motif_topology
import wrapper

class PathBuilder(object):
    def __init__(self):
        pass

    def build(self):
        f = open("all_points.str")
        line = f.readline()
        f.close()

        path = basic_io.str_to_points(line)

        mg = None

        f = open("mg.top")
        line = f.readline()
        f.close()

        mg = motif_graph.motif_graph_from_topology(line)

        segments = self._get_segments(path)
        pathes = self._get_sub_pathes(segments)

        if mg == None:
            mg = motif_graph.MotifGraph()


        w = wrapper.FollowPathWrapper()
        w.run(path="path.0.str", mg="mg.top")

        f = open("mt_out.top")
        line = f.readline()
        f.close()

        mt_all = motif_tree.motif_tree_from_topology_str(line)
        mg.add_motif_tree(mt_all)

        print "building:"
        for i in range(1, len(pathes)):

            print "path: ", i

            last_node = mg.last_node()
            s = mg.topology_to_str()
            f = open("mg_input.top", "w")
            f.write(s + "\n")
            f.write(str(last_node.index) + " " + last_node.data.ends[1].name() + "\n")
            f.close()

            w = wrapper.FollowPathWrapper()
            w.run(path="path."+str(i)+".str", mg="mg_input.top")

            f = open("mt_out.top")
            line = f.readline()
            f.close()

            mt = motif_tree.motif_tree_from_topology_str(line)

            mg.add_motif_tree(mt)
            mt_all.add_motif_tree(mt)


        mg.to_pdb("final_rna_path.pdb")
        f = open("mt_out.top", "w")
        f.write(mt_all.topology_to_str() + "\n")
        f.close()


    def _get_segments(self, path):

        direction = [0,0,0]
        new_direction = None
        segments = []
        segment = []
        for i, p in enumerate(path):
            if i < 2:
                segment.append(p)
                if i == 1:
                    direction = util.normalize(segment[0] - segment[1])
                continue

            new_direction = util.normalize(segment[-1] - p)
            if util.distance(new_direction, direction) > 0.1:
                segments.append(segment)
                segment = [p]
                direction = new_direction
            else:
                segment.append(p)

        if len(segment) > 0:
            segments.append(segment)

        return segments

    def _get_sub_pathes(self, segments):
        pathes = []
        for i in range(len(segments)):
            if i == 0:
                continue

            p = []
            if i == 1:
                p.extend(segments[0])
            else:
                half = len(segments[i-1])/2
                p.extend(segments[i-1][half-1:])

            if i == len(segments)-1:
                p.extend(segments[i])
            else:
                half = len(segments[i])/2
                p.extend(segments[i][:half-1])
            pathes.append(p)

        for i, p in enumerate(pathes):
            basic_io.points_to_pdb("path."+str(i)+".pdb", p)
            f = open("path."+str(i)+".str", "w")
            f.write(basic_io.points_to_str(p))
            f.close()

        return pathes