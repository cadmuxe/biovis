class LevenshteinDistance(object):
    """
    Levenshtein Distance
    Original from John Wenskovich in Java
    """
    def __init__(self, ins=1, delt=1, mod=1):
        self.__insertDistance = ins
        self.__deleteDistance = delt
        self.__modifyDistance = mod
 
    def updateWeights(self, ins, delt, mod):
        self.__insertDistance = ins
        self.__deleteDistance = delt
        self.__modifyDistance = mod

    def computeDistance(self, str1, str2):
        distance = [[0 for j in range(len(str2) + 1)] for i in range(len(str1) + 1)]
        for i in range(len(str1) + 1):
            distance[i][0] = i * self.__insertDistance
        for j in range(len(str2) + 1):
            distance[0][j] = j * self.__deleteDistance

        for i in range(1, len(str1) + 1):
            for j in range(1, len(str2) + 1):
		        
                if str1[i-1] == str2[j-1]:
                    modifyDist = 0
                else:
                    modifyDist = self.__modifyDistance
			    
                distance[i][j] = min( distance[i-1][j] + self.__insertDistance, distance[i][j-1] + self.__deleteDistance,
                    distance[i-1][j-1] + modifyDist )
        
        
        return distance[len(str1)][len(str2)]