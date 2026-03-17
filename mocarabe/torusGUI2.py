# add more colours/richer colour logic
# draw full path
# take into account  when enter and exit occurs at the same time

import tkinter as tk
import sys
import re

TIME = 0  # global, current frame time


def parseIndices(l):
    indexRegex = re.compile('(?<=\[)\d*(?=\])')
    enter = indexRegex.findall(l)
    indices = [int(x) for x in enter]
    return indices


def maxT(filename):
    solfile = open(filename, 'r')

    TMax = 0
    currentT = 0
    for line in solfile:
        match = re.compile('\d*(?=(] = 1$))').search(line)
        if match:
            currentT = int(match.group())
        if (currentT > TMax):
            TMax = currentT
    solfile.close()
    return TMax


class MainApplication(tk.Frame):

    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        if (len(sys.argv) != 2):
            sys.stderr.write(
                "Please enter a gurobi solution file as an argument\n")
            raise SystemExit

        filename = sys.argv[1]

        Nx = int(re.compile('(?<=Nx)\d*').search(filename).group())
        Ny = int(re.compile('(?<=Ny)\d*').search(filename).group())
        C = int(re.compile('(?<=C)\d*').search(filename).group())
        P = int(re.compile('(?<=P)\d*').search(filename).group())
        T = int(re.compile('(?<=T)\d*').search(filename).group())

        h = [[[[[0 for t in range(T)] for p in range(P)] for c in range(
            C)] for y in range(Ny)] for x in range(Nx)]
        v = [[[[[0 for t in range(T)] for p in range(P)] for c in range(
            C)] for y in range(Ny)] for x in range(Nx)]
        enter = [[[[0 for t in range(T)] for p in range(P)]
                  for y in range(Ny)] for x in range(Nx)]
        exit = [[[[0 for t in range(T)] for p in range(P)]
                 for y in range(Ny)] for x in range(Nx)]

        palette = ['green', 'purple', 'yellow', 'red', 'gold', 'orange', 'blue',
                   'khaki', 'light cyan', 'azure', 'greenyellow', 'deep sky blue']
        with open(filename) as f:
            lines = f.read().splitlines()
        for l in lines:
            if len(l) == 0:
                continue
            ind = parseIndices(l)
            if l[0] == 'h':
                h[ind[0]][ind[1]][ind[2]][ind[3]][ind[4]] = int(l[-1])
            elif l[0] == 'v':
                v[ind[0]][ind[1]][ind[2]][ind[3]][ind[4]] = int(l[-1])
            elif l[0:5] == 'enter':
                enter[ind[0]][ind[1]][ind[2]][ind[3]] = int(l[-1])
            elif l[0:4] == 'exit':
                exit[ind[0]][ind[1]][ind[2]][ind[3]] = int(l[-1])
            else:
                continue
        T = maxT(filename)  # actually want to use cycles used, not upper bound

        stepx = 70
        stepy = 70
        offsetx = 20
        offsety = 20
        arrowWidth = 3
        frame = tk.Frame(self)
        frame.pack()

        MAXHEIGHT = (Ny+1)*stepy+offsety
        w = tk.Canvas(self, width=Nx*stepx+offsetx, height=(Ny)*stepy+offsetx)
        w.pack()

        # Scrollbar (Ctrl + mousewheel to scroll horizontally)
        vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        w.bind('<4>', lambda event: w.yview('scroll', -1, 'units'))
        w.bind('<5>', lambda event: w.yview('scroll', 1, 'units'))
        w.bind('<Control-4>', lambda event: w.xview('scroll', -1, 'units'))
        w.bind('<Control-5>', lambda event: w.xview('scroll', 1, 'units'))

        def incrementTime():
            global TIME
            if (TIME < T - 1):
                TIME = TIME + 1
            drawCanvas(TIME)

        def decrementTime():
            global TIME
            if (TIME > 0):
                TIME = TIME - 1
            drawCanvas(TIME)

        # '-' button
        button1 = tk.Button(frame, text='-', command=decrementTime)
        button1.pack(side='left', padx=10)
        # cycle indicator
        timeString = tk.StringVar()
        currentTimeBox = tk.Label(frame, textvariable=timeString)
        # '+' button
        currentTimeBox.pack(side='left', padx=10)
        button2 = tk.Button(frame, text='+', command=incrementTime)
        button2.pack(side='left')

        def drawCanvas(time):
            w.delete("all")
            timeString.set(str(TIME))

            # Switches
            for x in range(0, Nx):
                for y in range(0, Ny):
                    x1 = stepx*x+offsetx
                    y1 = MAXHEIGHT-(stepy*(y+1)+offsety)
                    x2 = stepx*(x+1)
                    y2 = MAXHEIGHT-(stepy*(y+2))
                    w.create_rectangle(x1, y1, x2, y2)

                    for p in range(0, P):
                        for f in range(0, len(enter[x][y][p])):
                            if enter[x][y][p][time] == 1:
                                w.create_rectangle(x1, y1, x2, y2, fill="{}".format(
                                    palette[p % len(palette)]))
                            elif exit[x][y][p][time] == 1:
                                w.create_rectangle(x1, y1, x2, y2, fill="{}".format(
                                    palette[p % len(palette)]))
                    w.create_text((x1+x2)/2, (y1+y2)/2, text=str(x)+","+str(y))

            # Horizontal Routing
            for x in range(0, Nx):
                for y in range(0, Ny):
                    for c in range(0, C):
                        if (C > 1):  # increment, starting at a quarter of the switch
                            lowerBound = (offsety * 0.75 + (stepy)*(y+0.25))
                            y1 = y2 = lowerBound + \
                                ((c)*0.5 / float(C-1))*(stepy - offsety)
                        else:  # centre
                            centre = MAXHEIGHT-(stepy * (y + 1.5) + offsety/2)
                            y1 = y2 = centre
                        x1 = stepx*(x)
                        x2 = x1 + offsetx
                        drawn = False
                        for p in range(0, P):
                            if h[x][y][c][p][time] == 1:
                                drawn = True
                                w.create_line(x1, y1, x2, y2, fill="{}".format(palette[p % len(palette)]),
                                              width=arrowWidth, arrow=tk.LAST)
                                w.create_text(x1 + (offsetx / 2),
                                              y1, text="{}".format(p))
                        # if not drawn:
                            # w.create_line(x1, y1, x2, y2, fill="black", width=arrowWidth, arrow=tk.LAST)

            # Verical Routing
            for x in range(0, Nx):
                for y in range(0, Ny):
                    for c in range(0, C):
                        if (C > 1):  # increment, starting at a quarter of the switch
                            lowerBound = (offsetx * 0.75 + (stepx)*(x+0.25))
                            x1 = x2 = lowerBound + \
                                ((c)*0.5 / float(C-1))*(stepx - offsetx)
                        else:  # centre
                            centre = offsetx * 0.5 + (stepx)*(x+0.5)
                            x1 = x2 = centre
                        y1 = MAXHEIGHT - (stepy * (y + 1))
                        y2 = MAXHEIGHT - (stepy * (y + 1) + offsety)
                        drawn = False
                        for p in range(0, P):
                            if v[x][y][c][p][time] == 1:
                                drawn = True
                                w.create_line(x1, y1, x2, y2, fill="{}".format(palette[p % len(palette)]),
                                              width=arrowWidth, arrow=tk.LAST)
                                w.create_text(
                                    x1, y2 + (offsety / 2), text="{}".format(p))
                        # if not drawn:
                        #     w.create_line(x1, y1, x2, y2, fill="black", width=arrowWidth,arrow=tk.LAST)

        drawCanvas(0)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Torus GUI")
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
