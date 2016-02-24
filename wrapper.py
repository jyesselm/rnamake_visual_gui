import os, subprocess
from rnamake import base, option, util

class FollowPathWrapper(base.Base):
    def __init__(self):
        self.setup_options_and_constraints()

        if not os.environ.get('RNAMAKE'):
            raise ValueError("you might want to set RNAMAKE in your .bashrc")

        self.path = os.environ.get('RNAMAKE') + \
                    "/rnamake/lib/RNAMake/cmake/build/follow_path"

        if not os.path.isfile(self.path):
            raise  ValueError("follow_path program does not exist please compile c++ code")

    def setup_options_and_constraints(self):
        options = { 'path' : "",
                    'mg'  : "" }

        self.exec_options = { o : 1 for o in "path mg".split()}
        self.default_options = {}
        self.options = option.Options(options)
        for k in self.exec_options.keys():
            self.default_options[k] = self.option(k)

    def run(self, **options):
        self.options.dict_set(options)
        cmd = self._get_command()
        subprocess.call(cmd, shell=True)

    def _get_command(self):
        s = self.path
        for opt in self.exec_options.keys():
            val  = self.option(opt)
            dval = self.default_options[opt]
            if val == dval:
                continue

            s += " -" + opt + " " + val
        return s

if __name__ == "__main__":
    w = FollowPathWrapper()
    w.run(path="path.0.str")