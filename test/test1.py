import __main__
__main__.pymol_argv = [ 'pymol', '-qc'] # Quiet and no GUI

import sys, time, os
import pymol

pymol.finish_launching()




pymol.cmd.load("scTIM.pdb")
pymol.cmd.show("cartoon")
pymol.cmd.hide("lines")


#pymol.cmd.quit()
