__author__ = 'cadmuxe'

from SPaintWidget import color
import sys

class sequence(object):
    """
    sequence
    """
    def __init__(self, name, seq):
        self.__name = name.strip()
        self.__seq = seq.strip()
        self.weight = 0
    def __getattr__(self, item):
        if item =="seq":
            return self.__seq
        elif item == "name":
            return self.__name
    def __getitem__(self, item):
        return self.__seq[item]
    def __cmp__(self, other):
        return self.weight - other.weight
    def __len__(self):
        return len(self.__seq)
    def __iter__(self):
        return iter(self.__seq)




class sequenceSet(object):
    """
    Set of sequences
    """
    def __init__(self, filename=None):

        self.__sequence=[]
        self.__color = None
        if filename is not None:
            self.loadFromFile(filename)

    def loadFromFile(self,filename):
        f = open(filename)
        lines = f.readlines()
        f.close()
        for x in range(len(lines)):
            if lines[x][0] == '>':
                self.__sequence.append(sequence(lines[x][1:], lines[x+1]))
    def __getitem__(self, item):
        return self.__sequence[item]
    def __len__(self):
        return len(self.__sequence)
    def __iter__(self):
        return iter(self.__sequence)

    def updateColor(self, paintWidget):
        """
        update coloring to paintWidget, should execute one of *Color functions first
        """
        if self.__color is None:
            raise Exception("Need calculate color first")
        for i in range(len(self.__color)):
            paintWidget.update_color(i, self.__color[i])
        paintWidget.redraw_colors()

    def basicColor(self):
        """
        basic coloring, gray for '-', black for fragments
        """
        self.__color = []
        for seq in self.__sequence:
            cl =[]
            for s in seq:
                if s =='-':
                    cl.append(color.gray)
                else:
                    cl.append(color.black)
            self.__color.append(cl)

    def frequencyColor(self):
        """
        coloring the sequences, the fragment in the same column with the largest frequency are colored with red
        for other fragment, if the adjacent fragment(in the column) are same, they will be colored in same color
        """
        self._calculate_frag_frequency()
        self._sort_by_frag_frequency()
        # initialize __color to store result
        self.__color = [[] for i in range(len(self.__sequence))]
        pre_frag = ''
        pre_color = None
        for frag_id in range(len(self.frag_frequency)):
            for seq_id in range( len(self.__sequence)):
                try:
                    if self.__sequence[seq_id][frag_id] == '-':
                        pre_color = color.gray
                    elif self.__sequence[seq_id][frag_id] == self.frag_frequency[frag_id][1]:
                        pre_color = color.red       # coloring the largest frequency fragment in the column
                    elif self.__sequence[seq_id][frag_id] != pre_frag:
                        #if the previous fragment and the current is different, change a color
                        pre_color = color.random(pre_color)
                    self.__color[seq_id].append(pre_color)
                except IndexError:
                    pass
        return


    def _calculate_frag_frequency(self):
        """
        calculate the fragment which has the largest frequency in each column
        """
        # calculate the max length of sequence
        max_len = max([len(seq) for seq in self.__sequence])

        # store the frequency informaiton
        # [(fragmentId, fragment, frequency)]
        self.frag_frequency=[]
        for frag_id in range(max_len):
            frequency_list={}   # store the frequency of each kind of fragment(residue) in one colum
            for seq in self.__sequence:
                try:
                    if seq[frag_id] == '-':     # do not calculate '-'
                        continue
                    if frequency_list.has_key(seq[frag_id]):
                        frequency_list[seq[frag_id]] += 1
                    else:
                        frequency_list[seq[frag_id]] = 0
                # happened when seq do not long enough, can not assume all sequence have the same length
                except IndexError:
                    continue
            # find out the fragment that has largest frequency in each column and add them to the result
            m = max(frequency_list.values())
            for (frag, frequency) in frequency_list.items():
                if frequency == m:
                    self.frag_frequency.append((frag_id,frag, frequency))

    def _sort_by_frag_frequency(self):
        """
        sort sequences by the frag_frequency, a larger fragment frequency has a big weight
        """
        # find out the largest frequency and convert it to float type
        largest =  max(self.frag_frequency, key=lambda f:f[2])[2] * 1.0
        for seq in self.__sequence:
            for frag_id in range(len(seq)):
                if seq[frag_id] == self.frag_frequency[frag_id][1]:
                    seq.weight +=(self.frag_frequency[frag_id][2]/largest)
        # sort the sequence
        self.__sequence.sort(key=lambda seq:seq.weight, reverse = True)
