class sequenceCounter(object):
    """
    """
    def __init__(self):
        self.__residueCounter = [0 for i in range(26)]

    def addResidue(self, residue):
        intRepresentation = ord(residue)
        if 65 <= intRepresentation <= 90:
            intRepresentation -=65
        else:
            return
        self.__residueCounter[intRepresentation] +=1

    def getResidueCounts(self):
        return self.__residueCounter
