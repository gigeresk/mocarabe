# TODO

# ***better bounds on multidimensional lists (use a different data struct)
# add more colours/richer colour logic
# write N, P, F, T, etc. as lines in output rather than in file name

import Tkinter as tk
import sys
import re

TIME = 0  # global, current frame time


def parseIndices(l):
    indexRegex = re.compile('(?<=\[)\d*(?=\])')
    enter = indexRegex.findall(l)
    indices = [int(x) for x in enter]
    return indices


class MainApplication(tk.Frame):

    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        if (len(sys.argv) != 2):
            sys.stderr.write(
                "Please enter a gurobi solution file as an argument\n")
            exit()

        filename = sys.argv[1]

        Nx = int(re.compile('(?<=Nx)\d*').search(filename).group())
        Ny = int(re.compile('(?<=Ny)\d*').search(filename).group())
        X = Nx
        Y = Ny

        P = int(re.compile('(?<=P)\d*').search(filename).group())
        T = int(re.compile('(?<=T)\d*').search(filename).group())

        h = [[[[0 for t in range(T)] for p in range(P)]
              for y in range(Y)] for x in range(X)]
        v = [[[[0 for t in range(T)] for p in range(P)]
              for y in range(Y)] for x in range(X)]
        enter = [[[[0 for t in range(T)] for p in range(P)]
                  for y in range(Y)] for x in range(X)]
        exit = [[[[0 for t in range(T)] for p in range(P)]
                 for y in range(Y)] for x in range(X)]

        palette = ['green', 'purple', 'yellow', 'red',
                   'gold', 'orange', 'maroon', 'khaki']
        with open(filename) as f:
            lines = f.read().splitlines()
        for l in lines:
            if len(l) == 0:
                continue
            ind = parseIndices(l)
            if l[0] == 'h':
                h[ind[0]][ind[1]][ind[2]][ind[3]] = int(l[-1])
            elif l[0] == 'v':
                v[ind[0]][ind[1]][ind[2]][ind[3]] = int(l[-1])
            elif l[0:5] == 'enter':
                enter[ind[0]][ind[1]][ind[2]][ind[3]] = int(l[-1])
            elif l[0:4] == 'exit':
                exit[ind[0]][ind[1]][ind[2]][ind[3]] = int(l[-1])
            else:
                continue

        stepx = 70
        stepy = 70
        offsetx = 20
        offsety = 20
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
            for x in range(0, X):
                for y in range(0, Y):
                    for p in range(0, P):
                        x1 = stepx*x+offsetx
                        y1 = MAXHEIGHT-(stepy*(y+1)+offsety)
                        x2 = stepx*(x+1)
                        y2 = MAXHEIGHT-(stepy*(y+2))
                        w.create_rectangle(x1, y1, x2, y2)
                        for f in range(0, len(enter[x][y][p])):
                            if enter[x][y][p][time] == 1:
                                w.create_rectangle(x1, y1, x2, y2, fill="{}".format(
                                    palette[p % len(palette)]))
                            elif exit[x][y][p][time] == 1:
                                w.create_rectangle(x1, y1, x2, y2, fill="{}".format(
                                    palette[p % len(palette)]))
                            w.create_text((x1+x2)/2, (y1+y2)/2,
                                          text=str(x)+","+str(y))

            # Horizontal Routing
            for x in range(0, X):
                for y in range(0, Y):
                    x1 = stepx*(x)
                    x2 = x1 + offsetx
                    y1 = MAXHEIGHT-(stepy * (y + 1.375) + offsety)
                    y2 = y1
                    w.create_line(x1, y1, x2, y2, fill="black",
                                  width=5, arrow=tk.LAST)
                    for p in range(0, P):
                        for f in range(0, len(enter[x][y][p])):
                            if h[x][y][p][time] == 1:
                                w.create_line(x1, y1, x2, y2, fill="{}".format(palette[p % len(palette)]),
                                              width=5, arrow=tk.LAST)
                                w.create_text(x1 + (offsetx / 2),
                                              y1, text="{}".format(p))

            # Verical Routing
            for x in range(0, X):
                for y in range(0, Y):
                    x1 = stepx * (x + 0.375) + offsetx
                    x2 = x1
                    y1 = MAXHEIGHT-(stepy * (y + 1))
                    y2 = MAXHEIGHT-(stepy * (y + 1) + offsety)
                    w.create_line(x1, y1, x2, y2, fill="black",
                                  width=5, arrow=tk.LAST)
                    for p in range(0, P):
                        for f in range(0, len(enter[x][y][p])):
                            if v[x][y][p][time] == 1:
                                w.create_line(x1, y1, x2, y2, fill="{}".format(palette[p % len(palette)]),
                                              width=5, arrow=tk.LAST)
                                w.create_text(
                                    x1, y2 + (offsety / 2), text="{}".format(p))

        drawCanvas(0)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Torus GUI")
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
