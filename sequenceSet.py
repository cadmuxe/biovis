__author__ = 'cadmuxe'

from SPaintWidget import color
from LevenshteinDistance import LevenshteinDistance as LeveDist
from sequenceCounter import sequenceCounter

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
    def __init__(self, TIMs_filename=None, scTIM_filename=None):

        self.__sequence=[]
        self.__color = None
        if TIMs_filename is not None:
            self.loadTIMsFromFile(TIMs_filename)
        if scTIM_filename is not None:
            self.loadscTIMFromFile(scTIM_filename)

    def loadTIMsFromFile(self,filename):
        f = open(filename)
        lines = f.readlines()
        f.close()
        for x in range(len(lines)):
            if lines[x][0] == '>':
                self.__sequence.append(sequence(lines[x][1:], lines[x+1]))
        self.calculate_frag_frequency()
    def clear_weight(self):
        for seq in self.__sequence:
            seq.weight = 0
    def loadscTIMFromFile(self, filename):
        f = open(filename)
        self.__scTIM = sequence("scTIM",f.readline().strip())
        f.close()
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
                    cl.append(color.tetrad_red)
            self.__color.append(cl)

    def frequencyColor(self):
        """
        coloring the sequences, the fragment in the same column with the largest frequency 
        are colored with red for other fragment, if the adjacent fragment(in the column) 
        are same, they will be colored in same color
        """
        if not hasattr(self, "frag_frequency"):
            self.calculate_frag_frequency()
        # initialize __color to store result
        self.__color = [[] for i in range(len(self.__sequence))]
        for frag_id in range(len(self.max_frag_frequency)):
            for seq_id in range( len(self.__sequence)):
                try:
                    if self.__sequence[seq_id][frag_id] == '-':
                        fcolor = color.gray
                    elif self.__sequence[seq_id][frag_id] == self.max_frag_frequency[frag_id][1]:
                        # coloring the largest frequency fragment in the column
                        fcolor = color.tetrad_red
                    else:
                        fcolor = color.white
                    self.__color[seq_id].append(fcolor)
                except IndexError:
                    pass
        return
    def color_general_chemical(self):
        # initialize __color to store result
        self.__color = [[] for i in range(len(self.__sequence))]
        for frag_id in range(len(self.max_frag_frequency)):
            for seq_id in range( len(self.__sequence)):
                try:
                    if self.__sequence[seq_id][frag_id] == '-':
                        fcolor = color.gray
                    elif self.__sequence[seq_id][frag_id].upper() in ('G','A','V','L','I'):
                        # Aliphatic
                        fcolor = color.tetrad_red
                    elif self.__sequence[seq_id][frag_id].upper() in ('S','C','T','M'):
                        # HS
                        fcolor = color.tetrad_yellow
                    elif self.__sequence[seq_id][frag_id].upper() in ('P'):
                        # Cyclic
                        fcolor = color.tetrad_green
                    elif self.__sequence[seq_id][frag_id].upper() in ('F','W','Y'):
                        # Aromatic
                        fcolor = color.tetrad_blue
                    elif self.__sequence[seq_id][frag_id].upper() in ('H','K','R'):
                        # Basic
                        fcolor = color.white
                    elif self.__sequence[seq_id][frag_id].upper() in ('D','E','N','Q'):
                        #AA
                        fcolor = color.pink
                    else:
                        fcolor = color.black
                    self.__color[seq_id].append(fcolor)
                except IndexError:
                    pass
        return
    def color_side_chain_polarity(self):
        # initialize __color to store result
        self.__color = [[] for i in range(len(self.__sequence))]
        for frag_id in range(len(self.max_frag_frequency)):
            for seq_id in range( len(self.__sequence)):
                try:
                    if self.__sequence[seq_id][frag_id] == '-':
                        fcolor = color.gray
                    elif self.__sequence[seq_id][frag_id].upper() in ('A','C','G','I','L','M','F','P','W','V'):
                        # Nonpolar
                        fcolor = color.tetrad_red
                    elif self.__sequence[seq_id][frag_id].upper() in ('R','H','K'):
                        # Basic polar
                        fcolor = color.white
                    elif self.__sequence[seq_id][frag_id].upper() in ('N','Q','S','T','Y'):
                        # Polar
                        fcolor = color.tetrad_blue
                    elif self.__sequence[seq_id][frag_id].upper() in ('D','E'):
                        # Acidic polar
                        fcolor = color.tetrad_green
                    else:
                        fcolor = color.black
                    self.__color[seq_id].append(fcolor)
                except IndexError:
                    pass
        return
    def color_side_chain_charge(self):
        # initialize __color to store result
        self.__color = [[] for i in range(len(self.__sequence))]
        for frag_id in range(len(self.max_frag_frequency)):
            for seq_id in range( len(self.__sequence)):
                try:
                    if self.__sequence[seq_id][frag_id] == '-':
                        fcolor = color.gray
                    elif self.__sequence[seq_id][frag_id].upper() in ('A','N','C','Q','G','H','I','L','M','F','P','S','T','W','Y','V'):
                        # Neutral
                        fcolor = color.white
                    elif self.__sequence[seq_id][frag_id].upper() in ('R','K'):
                        # Positive
                        fcolor = color.tetrad_red
                    elif self.__sequence[seq_id][frag_id].upper() in ('D','E'):
                        # Negative
                        fcolor = color.tetrad_blue
                    else:
                        fcolor = color.black
                    self.__color[seq_id].append(fcolor)
                except IndexError:
                    pass
        return
    def color_side_chain_solvent(self):
        # initialize __color to store result
        self.__color = [[] for i in range(len(self.__sequence))]
        for frag_id in range(len(self.max_frag_frequency)):
            for seq_id in range( len(self.__sequence)):
                try:
                    if self.__sequence[seq_id][frag_id] == '-':
                        fcolor = color.gray
                    elif self.__sequence[seq_id][frag_id].upper() in ('R','K','D','E'):
                        # Charged
                        fcolor = color.tetrad_red
                    elif self.__sequence[seq_id][frag_id].upper() in ('Q','N','H','S','T','Y','C','M','W'):
                        # Polar
                        fcolor = color.tetrad_blue
                    elif self.__sequence[seq_id][frag_id].upper() in ('A','I','L','F','V','P','G'):
                        # Hydrophobic
                        fcolor = color.tetrad_green
                    else:
                        fcolor = color.black
                    self.__color[seq_id].append(fcolor)
                except IndexError:
                    pass
        return
    def color_selection(self, selections):
        """
        selections :{frag_id:frag_name}
        """
        self.__color = [[] for i in range(len(self.__sequence))]
        for frag_id in range(len(self.max_frag_frequency)):
            for seq_id in range( len(self.__sequence)):
                try:
                    if self.__sequence[seq_id][frag_id] == '-':
                        fcolor = color.gray
                    elif frag_id in selections.keys():
                        if self.__sequence[seq_id][frag_id] == selections[frag_id]:
                            fcolor = color.tetrad_red
                        else:
                            fcolor = color.white
                    else:
                        fcolor = color.black
                    self.__color[seq_id].append(fcolor)
                except IndexError:
                    pass
        return
    def color_common_with_scTim(self):
        frag_ids = range(1,300)
        selection ={}
        for (k,v) in zip(frag_ids, self.__scTIM):
            selection[k] = v
        self.color_selection(selection)


    def calculate_frag_frequency(self):
        """
        calculate the fragment which has the largest frequency in each column
        """
        # calculate the max length of sequence
        max_len = max([len(seq) for seq in self.__sequence])

        # store the frequency informaiton
        # [(fragmentId, fragment, frequency)]
        self.frag_frequency=[]
        self.max_frag_frequency=[]
        for frag_id in range(max_len):
            # store the frequency of each kind of fragment(residue) in one colum
            frequency_list={}   
            for seq in self.__sequence:
                try:
                    if seq[frag_id] == '-':     # do not calculate '-'
                        continue
                    if frequency_list.has_key(seq[frag_id]):
                        frequency_list[seq[frag_id]] += 1
                    else:
                        frequency_list[seq[frag_id]] = 0
                # happened when seq do not long enough, can not assume 
                # all sequence have the same length
                except IndexError:
                    continue
            # find out the fragment that has largest frequency in each column
            # and add them to the result

            m = max(frequency_list.values())
            self.frag_frequency.append(frequency_list)
            for (frag, frequency) in frequency_list.items():
                if frequency == m:
                    self.max_frag_frequency.append((frag_id,frag, frequency))
    def sort_by_selection(self, selections):
        """
        selections : {frag_id:frag_name}
        """
        self.clear_weight()
        for seq in self.__sequence:
            for frag_id in selections.keys():
                try:
                    if seq[frag_id] == selections[frag_id]:
                        seq.weight += 1
                except IndexError:
                    continue
        self.__sequence.sort(key=lambda seq:seq.weight, reverse = True)

    def sort_by_frag_frequency(self):
        """
        sort sequences by the frag_frequency, a larger fragment frequency has a big weight
        """
        # find out the largest frequency and convert it to float type
        self.clear_weight()
        if not hasattr(self, "max_frag_frequency"):
            self.calculate_frag_frequency()
        largest =  max(self.max_frag_frequency, key=lambda f:f[2])[2] * 1.0
        for seq in self.__sequence:
            for frag_id in range(len(seq)):
                if seq[frag_id] == self.max_frag_frequency[frag_id][1]:
                    seq.weight +=(self.max_frag_frequency[frag_id][2]/largest)
        # sort the sequence
        self.__sequence.sort(key=lambda seq:seq.weight, reverse = True)

    def sort_by_edit_dist(self):
        """
        Sort by edit distance from scTIM
        Original from John Wenskovitch in Java
        """
        self.clear_weight()
        leve  = LeveDist(1, 1, 1)
        for seq in self.__sequence:
            seq.weight = leve.computeDistance(seq.seq, self.__scTIM.seq)
        self.__sequence.sort(key=lambda seq:seq.weight, reverse = True)
    def sort_by_weighted_edit_dist(self):
        """
        Sort by weighted edit distance from scTIM
        again from John
        """
        self.clear_weight()
        leve = LeveDist(5, 5, 3)
        for seq in self.__sequence:
            seq.weight = leve.computeDistance(seq.seq, self.__scTIM.seq)
        self.__sequence.sort(key=lambda seq:seq.weight, reverse = True)

    def sort_by_num_of_common_residues_with_scTIM(self):
        """
        sort by number of residues in common with scTIM
        (single-sequence alignment)
        From John
        """
        self.clear_weight()
        for seq in self.__sequence:
            similarityCounter = 0
            for i in range(min(len(seq.seq), len(self.__scTIM.seq))):
                if seq.seq[i] == self.__scTIM.seq[i]:
                    similarityCounter += 1
            seq.weight = similarityCounter
        self.__sequence.sort(key=lambda seq:seq.weight, reverse = True)
    
    def sort_by_num_of_common_residues_with_scTIM_norm(self):
        """
        sort by percent of residues in common with scTIM
        (normalized single-sequence alignment)
        Hello John
        """
        self.clear_weight()
        for seq in self.__sequence:
            similarityPercentageCounter = 0.0
            for i in range(min(len(seq.seq), len(self.__scTIM.seq))):
                if seq.seq[i] == self.__scTIM.seq[i]:
                    similarityPercentageCounter += 1
            seq.weight = similarityPercentageCounter / len(seq.seq)
        self.__sequence.sort(key=lambda seq:seq.weight, reverse = True)
   
    def sort_by_number_of_common_residues_with_scTIM_without_position(self):
        """
        sort by number of residue in common with scTIM without consideration
        of sequence position
        @ John
        """
        self.clear_weight()
        scTIMCounter = sequenceCounter() 
        overallCount = 0

        for frag in self.__scTIM.seq:
            scTIMCounter.addResidue(frag)
        scTIMResidues = scTIMCounter.getResidueCounts()
        for seq in self.__sequence:
            counter = sequenceCounter()
            for frag in seq.seq:
                counter.addResidue(frag)
            loopResidues = counter.getResidueCounts()
            for k in range(26):
                if loopResidues[k] > scTIMResidues[k]:
                    overallCount += scTIMResidues[k]
                else:
                    overallCount += loopResidues[k]
            seq.weight = overallCount
    
    def sort_by_percent_of_common_residues_with_scTIM_without_position(self):
        """
        sort by percent of residue in common with scTIM without consideration
        of sequence position
        Hi John
        """
        self.clear_weight()
        scTIMCounter = sequenceCounter() 
        overallCount = 0
        scTIMPercentCount =0.0

        for frag in self.__scTIM.seq:
            scTIMCounter.addResidue(frag)
        scTIMResidues = scTIMCounter.getResidueCounts()
        for res in scTIMResidues:
            scTIMPercentCount += res
        for seq in self.__sequence:
            counter = sequenceCounter()
            for frag in seq.seq:
                counter.addResidue(frag)
            loopResidues = counter.getResidueCounts()
            for k in range(26):
                if loopResidues[k] > scTIMResidues[k]:
                    overallCount += scTIMResidues[k]
                else:
                    overallCount += loopResidues[k]
            seq.weight = overallCount/scTIMPercentCount

    def sort_by_number_of_residue_seq_of_len_n(self, n):
        """
        sort by number of residue sequences of length N in common
        Thank you John
        """
        self.clear_weight()
        for seq in self.__sequence:
            similarityLengthCounter = 0
            for i in range(min(len(seq.seq), len(self.__scTIM.seq))):
                if seq.seq[i:i+n] == self.__scTIM.seq[i:i+n]:
                    similarityLengthCounter += 1
            seq.weight = similarityLengthCounter
        self.__sequence.sort(key=lambda seq:seq.weight, reverse = True)
        

        
        

