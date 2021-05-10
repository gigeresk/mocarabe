class Box: #TODO move outof here
    negativeBox = [] #anything we do NOT want to enter using an h or v

    def __init__(self, start, end, modulo):
        del self.negativeBox[:]
        if end[0] < start[0] and end[1] < start[1]: # end comes before start in both x and y (must go over the edge twice)
            for x in range(0,modulo):
                for y in range(0,modulo):
                    if (x>end[0] and x<start[0]) or (y>end[1] and y<start[1]) or ( x==end[0] and y>end[1]):
                        self.negativeBox.append( (x,y) )
        elif end[0] < start[0]: #end comes before start in x dir only
            for x in range(0,modulo):
                for y in range(0, modulo):
                    if (x<start[0] and x>end[0]) or (y>end[1]) or (y<start[1]):
                        self.negativeBox.append( (x, y) )
        elif end[1] < start[1]: #end comes before start in y dir only
            for x in range(0,modulo):
                for y in range(0, modulo):
                    if (y<start[1] and y>end[1]) or (x>end[0]) or (x<start[0]):
                        self.negativeBox.append( (x, y) )
        else:
            # D.x > S.x, D.y > S.y, simple case
            for x in range(0, modulo):
                for y in range(0, modulo):
                    if( x > end[0] or y > end[1]) or ( x < start[0] or y < start[1] ):
                        self.negativeBox.append( (x,y) )

        self.negativeBox.append( (start[0],start[1]) ) #add start

    def prints(self):
        print(self.negativeBox)

