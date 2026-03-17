# add more colours/richer colour logic
# draw full path
# take into account  when enter and exit occurs at the same time

import tkinter as tk
import re
import argparse
import ast
import numpy as np

try:
    import pyscreenshot as ImageGrab

    # might need to do sudo apt-get install python3-pil.imagetk
    from PIL import ImageTk, Image
except:
    print(
        "I think you might have to do a little $sudo apt-get install python3-pil.imagetk"
    )
try:
    import canvasvg
except:
    print("pip3 install canvasvg")
try:
    import palettable
except:
    print("pip3 install palettable")

TIME = 0  # global, current frame time
parser = argparse.ArgumentParser(
    description="GUI for cgra-ilp. This version has no time cycling"
)
parser.add_argument("-sched", type=str, help="sol file for the GUI to visualize")
parser.add_argument(
    "--zoom",
    type=int,
    default=2,
    help="magnify everything in the GUI, except for the arrows",
)
parser.add_argument("--net", type=str, help="Netlist for labelling operators, etc. ")
parser.add_argument("--proj", type=str, help="proj directory", required=True)
parser.add_argument("-o", type=str, default="", help="export SVG path ")  # TODO

DEBUG = False
# https://jiffyclub.github.io/palettable/colorbrewer/
# change the palette here
palette = palettable.tableau.Tableau_20.hex_colors


def parseIndices(l):
    indexRegex = re.compile("(?<=\[)\d*(?=\])")
    enter = indexRegex.findall(l)
    indices = [int(x) for x in enter]
    return indices


def maxT(filename):
    solfile = open(filename, "r")

    TMax = 0
    currentT = 0
    for line in solfile:
        match = re.compile("\d*(?=(] = 1$))").search(line)
        if match:
            currentT = int(match.group())
        if currentT > TMax:
            TMax = currentT
    solfile.close()
    return TMax


def get_P_to_node_map(file_name):
    D = 0
    f = open(file_name, "r")
    lines = f.read().splitlines()
    maxP = len(lines) + 1  # number of nets = number of lines in the file
    fanout = [0] * maxP
    src_x = [0] * maxP
    src_y = [0] * maxP
    import collections

    P_to_node_map = collections.OrderedDict()
    for p, line in enumerate(lines):
        rawnet = ast.literal_eval(line)
        net = np.array(rawnet)

        P_to_node_map[str(p)] = net

    return P_to_node_map


def get_node_id_dest(p, x, y, P_to_node_map):
    fanout = P_to_node_map[str(p)]
    for arr in fanout:
        if arr[0] == x and arr[1] == y:
            return arr[2]

    return -1


def get_node_id_source(p, x, y, P_to_node_map):
    fanout = P_to_node_map[str(p)]
    arr = fanout[0]
    if arr[0] == x and arr[1] == y:
        return arr[2]

    return -1


class MainApplication(tk.Frame):
    def draw_switch(self, canvas, switch_x, switch_y):
        # bounding box
        canvas.create_rectangle(
            switch_x,
            switch_y,
            switch_x + self.switch_image_width,
            switch_y + self.switch_image_height,
            fill="",
        )

        # NW to SE
        canvas.create_line(
            # top x line
            switch_x + 0.1 * self.switch_image_width,
            switch_y + 0.2 * self.switch_image_height,
            switch_x + 0.3 * self.switch_image_width,
            switch_y + 0.2 * self.switch_image_height,
            # NW to SE diagonal
            switch_x + 0.7 * self.switch_image_width,
            switch_y + 0.8 * self.switch_image_height,
            # bottom x line
            switch_x + 0.9 * self.switch_image_width,
            switch_y + 0.8 * self.switch_image_height,
        )

        # SW to NE
        canvas.create_line(
            # bottom x line
            switch_x + 0.1 * self.switch_image_width,
            switch_y + 0.8 * self.switch_image_height,
            switch_x + 0.3 * self.switch_image_width,
            switch_y + 0.8 * self.switch_image_height,
            # SW to NE diagonal
            switch_x + 0.7 * self.switch_image_width,
            switch_y + 0.2 * self.switch_image_height,
            # top x line
            switch_x + 0.9 * self.switch_image_width,
            switch_y + 0.2 * self.switch_image_height,
        )

    def draw_table_to_switch(self, canvas, startx, starty, endx, endy, p, c, direction):

        # direction = "E" or "N"
        drawXLine = True
        # line from cycle table to switch point
        canvas.create_line(
            startx,
            starty,
            endx,
            starty + (endy - starty) / 2,
            endx,
            endy,
            width=12,
            smooth="true",
            fill="{}".format(palette[p % len(palette)]),
        )

    def draw_curved_exit_noc(self, canvas, startx, starty, endx, endy, p):
        arrowWidth = 12
        drawXLine = True
        canvas.create_arc(
            startx,
            starty,
            endx,
            endy,
            start=0,
            extent=90,
            width=arrowWidth,
            style="arc",
            outline="{}".format(palette[p % len(palette)]),
        )  # width=arrowWidth)#, arrow=tk.LAST)
        # xline
        if drawXLine:
            canvas.create_line(
                endx - ((endx - startx) / 2),
                starty,
                startx,  # + self.x_reg_table_width,
                starty,
                width=arrowWidth,
                # arrow=tk.LAST,
                # arrowshape=arrowshaper,
                fill="{}".format(palette[p % len(palette)]),
            )
        # yline
        canvas.create_line(
            endx,
            starty + ((endy - starty) / 2),
            endx,
            endy,  # starty + self.switch_image_height,
            width=arrowWidth,
            # arrow=tk.LAST,
            fill="{}".format(palette[p % len(palette)]),
        )

    def get_x1(self, x):
        return self.stepx * (x) + self.offsetx

    def get_x2(self, x):
        return self.stepx * (x + 1)

    def get_y1(self, y):
        return self.MAXHEIGHT - (self.stepy * (y + 1) + self.offsety)

    def get_y2(self, y):
        return self.MAXHEIGHT - (self.stepy * (y + 2))

    # exit reg table
    # TODO rename...
    def get_exit_table_y1(self, y, t):
        return self.get_y2(y) + ((t + 1) * (self.stepy - self.offsety) / (2 * self.T))

    def get_exit_table_y2(self, y, t):
        return self.get_y2(y) + ((t) * (self.stepy - self.offsety) / (2 * self.T))

    # exit reg curve
    def get_exit_curve_y1(self, y, t):
        return (self.get_exit_table_y1(y, t) + self.get_exit_table_y2(y, t)) / 2

    def get_exit_curve_y2(self, y, c):
        return self.get_y1(y) - (c + 1) * self.switch_image_height

    # switch
    def get_switch_x1(self, x, c):
        return self.get_x1(x) + (c + 1) * self.switch_image_width

    # Channel arrows
    # h
    def get_h_channel_x1(self, x, c):
        return (self.stepx * x) - (c * self.switch_image_width)

    def get_h_channel_x2(self, x, c):
        return self.get_x2(x) - (c + 1) * self.switch_image_width

    def get_h_channel_y(self, y, c, t):
        switch_y = self.get_y1(y) - (c + 1) * self.switch_image_height
        return switch_y + ((t + (self.T / 2)) / (2 * self.T)) * self.switch_image_height

    def h_channel_start_y(self, y, c):
        print("get rid of h_channel_start_y")
        return self.MAXHEIGHT - (self.stepy * (y)) + (c + 1) * self.switch_image_height

    # v
    def get_v_channel_y1(self, y, c):
        y1 = self.get_y1(y - 1)
        return y1 - (c + 1) * self.switch_image_width

    def get_v_channel_y2(self, y, c):
        y2 = self.MAXHEIGHT - (self.stepy * (y + 1) + self.offsety)
        return y2 - (c + 0) * self.switch_image_width

    def get_v_channel_x(self, x, c, t):
        T = self.T
        switch_x = self.get_x2(x) - (c + 1) * self.switch_image_width
        return switch_x + ((t + (T / 2)) / (2 * T)) * self.switch_image_width

    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        args = parser.parse_args()
        sched_dir = args.proj + "schedule/"
        import glob
        import os

        sched_file = glob.glob(sched_dir + "*.sol")
        assert len(sched_file) != 0, "Need at least one *.sol file in " + str(sched_dir)
        assert len(sched_file) == 1, "Should only be one *.sol file in " + str(
            sched_dir
        )
        sched_file = sched_file[0]

        netlist_dir = args.proj + "netlist/"
        netlist_filename = glob.glob(netlist_dir + "*.net")
        assert len(netlist_filename) != 0, "Need at least one *.net file in " + str(
            netlist_dir
        )
        assert len(netlist_filename) == 1, "Should only be one *.net file in " + str(
            netlist_dir
        )

        netlist_filename = netlist_filename[0]
        # import pdb; pdb.set_trace()
        # filename = args.sched
        if args.zoom:
            ZOOM = args.zoom

        print("filename:", sched_file)
        assert os.path.exists(sched_file), f"Schedule path {sched_file} does not exist"

        basename = os.path.basename(sched_file)
        # todo header
        Nx = int(re.compile("(?<=Nx)\d*").search(basename).group())
        Ny = int(re.compile("(?<=Ny)\d*").search(basename).group())
        C = int(re.compile("(?<=C)\d*").search(basename).group())
        P = int(re.compile("(?<=P)\d*").search(basename).group())
        T = int(re.compile("(?<=T)\d*").search(basename).group())

        print("Nx: ", Nx)
        print("Ny: ", Ny)
        print("C: ", C)
        print("P: ", P)
        print("T: ", T)

        h = [
            [
                [[[0 for t in range(T)] for p in range(P)] for c in range(C)]
                for y in range(Ny)
            ]
            for x in range(Nx)
        ]
        v = [
            [
                [[[0 for t in range(T)] for p in range(P)] for c in range(C)]
                for y in range(Ny)
            ]
            for x in range(Nx)
        ]
        enter = [
            [
                [[[0 for t in range(T)] for p in range(P)] for c in range(C)]
                for y in range(Ny)
            ]
            for x in range(Nx)
        ]
        exit = [
            [
                [[[0 for t in range(T)] for p in range(P)] for c in range(C)]
                for y in range(Ny)
            ]
            for x in range(Nx)
        ]

        # first, get labels and ops ready
        operators = {}
        labels = {}
        net_label = {}
        if netlist_filename != None:
            with open(netlist_filename) as netlist_file:
                for line_count, line in enumerate(netlist_file):
                    net = line.partition("#")[0]
                    rawnet = ast.literal_eval(net)
                    for ix, vertex in enumerate(rawnet):
                        net_label[(rawnet[ix][0], rawnet[ix][1], line_count)] = rawnet[
                            ix
                        ][3]

                # edge_list = line.partition('#')[0] # comments

                # rawnet=ast.literal_eval(edge_list)
                # print
                # operator = ""
                # edge_operator = re.search('(?<=#operator{).?.?.?.?(?=})', line)
                # if edge_operator:
                #     operator = edge_operator.group()
                #     operators[str(rawnet[0][2])] = operator
                # label = ""
                # edge_label = re.search('(?<=#label{)([a-z]|[0-9]|\.)*(?=})', line)
                # if edge_label:
                #     label = edge_label.group()
                #     labels[str(rawnet[0][2])] = label
                #     # DO THIS FOR RETURN VAL TOO...
        with open(sched_file) as f:
            lines = f.read().splitlines()
        for l in lines:
            if len(l) == 0:
                continue
            ind = parseIndices(l)
            if l[0] == "h":
                h[ind[0]][ind[1]][ind[2]][ind[3]][ind[4]] = int(l[-1])
            elif l[0] == "v":
                v[ind[0]][ind[1]][ind[2]][ind[3]][ind[4]] = int(l[-1])
            elif l[0:6] != "enterc" and l[0:5] == "enter":
                enter[ind[0]][ind[1]][ind[2]][ind[3]][ind[4]] = int(l[-1])
            elif l[0:5] != "exitc" and l[0:4] == "exit":
                exit[ind[0]][ind[1]][ind[2]][ind[3]][ind[4]] = int(l[-1])
            else:
                continue

        # actually want to use cycles used, not upper bound
        T = maxT(sched_file) + 1
        self.T = T
        # deserialize labels
        # right now, assume PE has fixed label
        # serialized_label_file = open( serialized_labels, "r" )
        # deserialized_labels = serialized_label_file.read()
        # print( deserialized_labels )
        # labels = json.loads( deserialized_labels )

        # deserialize ops
        # serialized_operator_file = open( args.ops, "r" )
        # deserialized_operators = serialized_operator_file.read()
        # print( deserialized_operators )
        # operators = json.loads( deserialized_operators )

        arrowshaper = (20, 20, 20)

        # process netlist
        if netlist_filename != None:
            # import pdb; pdb.set_trace()
            P_to_node_map = get_P_to_node_map(netlist_filename)

            # dimensions
        # fraction of (x,y) square taken up by switches
        fraction_square_switch = 0.5

        # pixel counting
        base_stepx = 70
        base_stepy = 70
        base_offsetx = 10
        base_offsety = 10
        self.stepx = base_stepx * ZOOM
        self.stepy = base_stepy * ZOOM
        self.offsetx = base_offsetx * ZOOM
        self.offsety = base_offsety * ZOOM

        offsetx = base_offsetx * ZOOM
        offsety = base_offsety * ZOOM
        arrowWidth = 12
        self.switch_image_height = (
            (base_stepx - base_offsetx) * fraction_square_switch * ZOOM * (1 / C)
        )
        self.switch_image_width = (
            (base_stepy - base_offsety) * fraction_square_switch * ZOOM * (1 / C)
        )

        self.switch_image_height = int(self.switch_image_height)
        self.switch_image_width = int(self.switch_image_width)

        self.torus_loop_arc_vertical_box_height = self.stepx / 10
        frame = tk.Frame(self)
        frame.pack()

        self.MAXHEIGHT = (Ny + 1) * self.stepy + offsety
        canvas = tk.Canvas(
            self,
            width=Nx * self.stepx + 3 * offsetx,
            height=(Ny) * self.stepy + 3 * offsetx,
        )
        self._canvas = canvas
        canvas.configure(background="white")
        canvas.pack()

        # Scrollbar (Ctrl + mousewheel to scroll horizontally)
        vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.bind("<4>", lambda event: canvas.yview("scroll", -1, "units"))
        canvas.bind("<5>", lambda event: canvas.yview("scroll", 1, "units"))
        canvas.bind("<Control-4>", lambda event: canvas.xview("scroll", -1, "units"))
        canvas.bind("<Control-5>", lambda event: canvas.xview("scroll", 1, "units"))

        # PE box at every (x,y)
        for x in range(0, Nx):
            for y in range(0, Ny):
                self.x_reg_table_width = (
                    (self.stepx - self.offsetx) * (1 - fraction_square_switch) / 2
                )
                self.y_reg_table_height = (self.stepy - self.offsety) / (2 * T)

                # PE box
                canvas.create_rectangle(
                    self.get_x1(x), self.get_y1(y), self.get_x2(x), self.get_y2(y)
                )

                for p in range(0, P):
                    drawn = False
                    for t in range(0, T):
                        for c in range(0, C):
                            if exit[x][y][c][p][t] == 1:
                                drawn = True
                                node_id = 0
                                if netlist_filename != None:
                                    node_id = get_node_id_source(p, x, y, P_to_node_map)

                                color = palette[p % len(palette)]
                                # 'exit noc' PE slot
                                print("todo for more channels")
                                # canvas.create_rectangle(
                                #     self.get_x1( x ),
                                #     self.get_exit_table_y1( y, t ),
                                #     self.get_x1( x ) + self.x_reg_table_width,
                                #     self.get_exit_table_y2( y, t ),
                                #     fill="{}".format( color ))
                                if x == 0 and y == 0:
                                    canvas.create_text(
                                        self.get_x1(x)
                                        - self.x_reg_table_width / 2
                                        - 25,
                                        self.get_exit_table_y1(y, t)
                                        - self.y_reg_table_height / 2
                                        + 4,
                                        text=f"CTX {t}",
                                        font=f"Times {6 * ZOOM}",
                                        # fill="{}".format( color ))
                                    )
                                    canvas.create_line(
                                        self.get_x1(x),
                                        self.get_exit_table_y1(y, t)
                                        - self.y_reg_table_height / 2,
                                        self.get_x1(x) + self.x_reg_table_width,
                                        self.get_exit_table_y1(y, t)
                                        - self.y_reg_table_height / 2,
                                        width=6,
                                        arrow=tk.LAST,
                                        arrowshape=arrowshaper,
                                        fill="black",
                                    )

                                    canvas.create_line(
                                        self.get_x1(x),
                                        self.get_exit_table_y1(y, t)
                                        - self.y_reg_table_height / 2,
                                        self.get_x1(x) + self.x_reg_table_width,
                                        self.get_exit_table_y1(y, t)
                                        - self.y_reg_table_height / 2,
                                        width=6,
                                        arrow=tk.LAST,
                                        arrowshape=arrowshaper,
                                        fill="black",
                                    )

                                    # canvas.create_text(
                                    #         self.get_x1( x ) +(self.stepx-offsetx)/8,# (2*offsetx/8),
                                    #         self.get_exit_table_y2( y, t ) + (self.get_exit_table_y1( y, t )-self.get_exit_table_y2( y, t ))/4,
                                    #         font=f"Times {int(6*ZOOM)}",
                                    #         text=net_label[(x,y,p)].split(',')[0].rstrip()
                                    #     )
                                if x == 1 and y == 0:
                                    if c == 0:
                                        canvas.create_rectangle(
                                            self.get_x1(x),
                                            self.get_exit_table_y1(y, t)
                                            + (
                                                self.get_exit_table_y2(y, t)
                                                - self.get_exit_table_y1(y, t)
                                            )
                                            / 2,
                                            self.get_x1(x) + self.x_reg_table_width,
                                            self.get_exit_table_y2(y, t),
                                            fill="{}".format(color),
                                        )
                                    # TODO FOR MULT CHANNELS
                                    if c == 1:
                                        canvas.create_rectangle(
                                            self.get_x1(x),
                                            self.get_exit_table_y1(y, t),
                                            self.get_x1(x) + self.x_reg_table_width,
                                            self.get_exit_table_y1(y, t)
                                            + (
                                                self.get_exit_table_y2(y, t)
                                                - self.get_exit_table_y1(y, t)
                                            )
                                            / 2,
                                            fill="{}".format(color),
                                        )

                                if (T == 1) or enter[x][y][c][p][t - 1] != 1:
                                    self.draw_curved_exit_noc(
                                        canvas,
                                        self.get_x1(x) + self.x_reg_table_width,
                                        self.get_exit_curve_y1(y, t),
                                        # vary up to almost a third of the image width
                                        self.get_x2(x)
                                        - ((T - t) / T)
                                        * (0.28)
                                        * self.switch_image_width
                                        - (c) * self.switch_image_width,
                                        self.get_exit_curve_y2(y, c),
                                        p,
                                    )

                                if (x, y, p) in net_label and net_label[
                                    (x, y, p)
                                ] not in ["*", "+"]:
                                    if c == 0:
                                        canvas.create_text(
                                            # (2*offsetx/8),
                                            self.get_x1(x) + (self.stepx - offsetx) / 8,
                                            self.get_exit_table_y2(y, t)
                                            + (
                                                self.get_exit_table_y1(y, t)
                                                - self.get_exit_table_y2(y, t)
                                            )
                                            / 4,
                                            font=f"Times {int(6 * ZOOM)}",
                                            text=net_label[(x, y, p)]
                                            .split(",")[0]
                                            .rstrip(),
                                        )
                                    elif c == 1:
                                        canvas.create_text(
                                            # (2*offsetx/8),
                                            self.get_x1(x) + (self.stepx - offsetx) / 8,
                                            self.get_exit_table_y1(y, t)
                                            + (
                                                self.get_exit_table_y2(y, t)
                                                - self.get_exit_table_y1(y, t)
                                            )
                                            / 4,
                                            font=f"Times {int(6 * ZOOM)}",
                                            text=net_label[(x, y, p)]
                                            .split(",")[0]
                                            .rstrip(),
                                        )
                            elif enter[x][y][c][p][t] == 1:
                                # drawn = True

                                towards_switch_y = (
                                    self.get_y1(y) - (c + 1) * self.switch_image_height
                                )
                                node_id = 0
                                if netlist_filename != None:
                                    node_id = get_node_id_dest(p, x, y, P_to_node_map)

                                # 'enter noc' PE slot
                                canvas.create_rectangle(
                                    self.get_x1(x) + self.x_reg_table_width,
                                    self.get_exit_table_y1(y, t),
                                    (self.get_x1(x) + self.get_x2(x)) / 2,
                                    self.get_exit_table_y2(y, t),
                                    fill="{}".format(palette[p % len(palette)]),
                                )

                                if (x, y, p) in net_label:
                                    canvas.create_text(
                                        # self.get_x1( x ) + (offsetx/3),
                                        self.get_x1(x) + 3 * (self.stepx - offsetx) / 8,
                                        # (self.get_exit_table_y1( y, t ) + self.get_exit_table_y2( y, t ))/2,
                                        self.get_exit_curve_y1(y, t),
                                        font=f"Times {int(6 * ZOOM)}",
                                        text=net_label[(x, y, p)].split(",")[0],
                                    )

                                if exit[x][y][c][p][(t + 1) % T] != 1:
                                    # not a self-message

                                    pivotx = (
                                        self.get_x1(x)
                                        + 2 * self.x_reg_table_width
                                        + (1 / 8) * self.switch_image_width
                                    )

                                    if (
                                        t < T
                                        and h[(x + 1) % Nx][y][c][p][(t + 1) % T] == 1
                                    ):
                                        # EAST
                                        switch_y = (
                                            self.get_y1(y)
                                            - (c + 1) * self.switch_image_height
                                        )
                                        if x == 0 and y == 0:
                                            canvas.create_arc(
                                                # startx-100,#ENTERNOC RIGHT SIDE
                                                self.get_x1(x)
                                                + 2 * self.x_reg_table_width,
                                                self.get_exit_table_y1(y, t)
                                                - self.switch_image_height,
                                                # # -100+self.get_y1( y )  - ( c + 1 ) * self.switch_image_height, #ENTERNOC RIGHT
                                                # pivotx,
                                                # switch_y + (((t+1)+(T/2))/(2*T)) * self.switch_image_height,
                                                self.get_h_channel_x1(x + 1, c) + 80,
                                                self.get_h_channel_y(y, c, t) - 20,
                                                # switch_y  + (((t+1)+(T/2))/(2*T)) * self.switch_image_height,
                                                width=2,
                                                style="arc",
                                                start=-180,
                                                extent=90,
                                                # smooth="true",
                                                outline="{}".format(
                                                    palette[p % len(palette)]
                                                ),
                                            )

                                    if (
                                        t < T
                                        and v[x][(y + 1) % Ny][c][p][(t + 1) % T] == 1
                                    ):
                                        # NORTH
                                        a = 1
                                        # TODO fix

                                        # todo draw CURVED enter noc
                                        pivotx = 0
                                        if c == 1 and t == 0:
                                            pivotx = (
                                                self.get_x1(x)
                                                + 2.2 * self.x_reg_table_width
                                            )
                                        elif c == 1 and t == 1:
                                            pivotx = (
                                                self.get_x1(x)
                                                + 1 * self.x_reg_table_width
                                            )
                                        else:
                                            pivotx = (
                                                self.get_x1(x)
                                                + 3 * self.x_reg_table_width,
                                            )
                                        pivoty = (
                                            self.get_v_channel_y2(y, c)
                                            - self.stepy / 4,
                                        )
                                        canvas.create_line(
                                            self.get_x1(x) + 2 * self.x_reg_table_width,
                                            self.get_exit_table_y1(y, t),
                                            pivotx,
                                            pivoty,
                                            self.get_v_channel_x(x, c, (t + 1) % T),
                                            # self.get_v_channel_y2(y,c) - self.stepy/8,
                                            self.get_v_channel_y1(y + 1, c),
                                            # self.get_x1( x ) + 2*self.x_reg_table_width + (1/8)*self.switch_image_width,
                                            # pivotx,
                                            width=12,
                                            smooth="true",
                                            fill="{}".format(palette[p % len(palette)]),
                                        )

                                # else:
                                #     # self-message
                                #     # unsure if this is still valid
                                #     canvas.create_line(
                                #         self.get_x1( x ) + self.x_reg_table_width,
                                #         self.get_exit_table_y1( y, t),
                                #         self.get_x1( x ),
                                #         self.get_exit_curve_y1( y, t) + self.y_reg_table_height,
                                #         fill="{}".format( palette[p % len( palette )]),
                                #         width=arrowWidth, arrow=tk.LAST,
                                #         arrowshape=arrowshaper)

                # Switches in the rectangle
                for c in range(0, C):
                    self.draw_switch(
                        canvas,
                        self.get_x2(x) - (c + 1) * self.switch_image_width,
                        self.get_y1(y) - (c + 1) * self.switch_image_height,
                    )

                # cycle count text
                # for t in range(0, T):
                #     canvas.create_text(
                #         self.get_x1( x ) - (self.offsetx/10),
                #         self.get_exit_curve_y1( y, t),
                #         text="{}".format( t ) )
                # enter/exit noc text
                # canvas.create_text(
                #         self.get_x1( x ) + 0.5*self.x_reg_table_width,
                #         self.get_y2( y ) - 0.25*self.y_reg_table_height,
                #         font=f"Times {3*ZOOM}",
                #         text="enter PE" )
                # canvas.create_text(
                #         self.get_x1( x ) + 1.5*self.x_reg_table_width,
                #         self.get_y2( y ) - 0.25*self.y_reg_table_height,
                #         font=f"Times {3*ZOOM}",
                #         text="exit PE" )

        # Horizontal Routing arrows
        # TODO fix something about x2?
        for x in range(0, Nx + 1):
            for y in range(0, Ny):
                for c in range(0, C):
                    for t in range(0, T):
                        drawn = False
                        for p in range(0, P):
                            if (
                                x < Nx
                                and h[x][y][c][p][t] == 1
                                or x == Nx
                                and h[0][y][c][p][t] == 1
                            ):
                                if DEBUG:
                                    print(
                                        "h[{0}][{1}][{2}][{3}][{4}] = 1".format(
                                            x, y, c, p, t
                                        )
                                    )
                                drawn = True
                                canvas.create_line(
                                    self.get_h_channel_x1(x, c),
                                    self.get_h_channel_y(y, c, t),
                                    self.get_h_channel_x2(x, c),
                                    self.get_h_channel_y(y, c, t),
                                    fill="{0}".format(palette[p % len(palette)]),
                                    width=arrowWidth,
                                    arrow=tk.LAST,
                                    arrowshape=arrowshaper,
                                )

                                # just passing through, horizontal to horizontal
                                if h[(x + 1) % Nx][y][c][p][(t + 1) % T] == 1:
                                    # TODO eliminate
                                    switch_x2 = (
                                        self.get_x2(x)
                                        - (c + 1) * self.switch_image_width
                                    )

                                    canvas.create_line(
                                        self.get_h_channel_x2(x, c),
                                        self.get_h_channel_y(y, c, t),
                                        switch_x2 + self.switch_image_width,
                                        self.get_h_channel_y(y, c, t + 1),
                                        fill="{0}".format(palette[p % len(palette)]),
                                        width=arrowWidth,
                                    )

                                # just passing through, horizontal to vertical
                                if v[x % Nx][(y + 1) % Ny][c][p][(t + 1) % T] == 1:
                                    # TODO eliminate
                                    switch_x2 = (
                                        self.get_x2(x)
                                        - (c + 1) * self.switch_image_width
                                    )
                                    switch_x = (
                                        self.get_x1(x)
                                        - (c + 1) * self.switch_image_width
                                    )

                                    t_plus_1_switch_x = (
                                        switch_x
                                        + ((t + (T / 2)) / (2 * T))
                                        * self.switch_image_width
                                    )

                                    # canvas.create_line(
                                    #     switch_x2,
                                    #     self.get_h_channel_y( y, c, t ),
                                    #     t_plus_1_switch_x,
                                    #     self.get_h_channel_y( y, c, t )+50,
                                    #     fill="{0}".format( palette[p % len( palette )]),
                                    #     width=arrowWidth )
                        if not drawn:
                            # If unused in this cycle, draw a gray arrow
                            if x == 0:
                                canvas.create_line(
                                    self.get_h_channel_x1(x, c) - 300,
                                    self.get_h_channel_y(y, c, t),
                                    self.get_h_channel_x2(x, c),
                                    self.get_h_channel_y(y, c, t),
                                    fill="light gray",
                                    width=4,
                                    arrow=tk.LAST,
                                    arrowshape=arrowshaper,
                                )
                            else:
                                canvas.create_line(
                                    self.get_h_channel_x1(x, c),
                                    self.get_h_channel_y(y, c, t),
                                    self.get_h_channel_x2(x, c),
                                    self.get_h_channel_y(y, c, t),
                                    fill="light gray",
                                    width=4,
                                    arrow=tk.LAST,
                                    arrowshape=arrowshaper,
                                )
                        # if t==0:
                        #     # write a little '0' to indicate start cycle
                        #     canvas.create_text(
                        #         self.get_h_channel_x1( x, c) - (self.switch_image_width/10),
                        #         self.get_h_channel_y( y, c, t ),
                        #         font=f"Times {int(2*ZOOM)}",
                        #         text='0')
        # Verical Routing arrows
        # TODO draw 'just passing through'
        for x in range(0, Nx):
            for y in range(0, Ny + 1):
                for c in range(0, C):
                    for t in range(0, T):
                        drawn = False
                        for p in range(0, P):
                            if (
                                y < Ny
                                and v[x][y][c][p][t] == 1
                                or (y == Ny and v[x][0][c][p][t] == 1)
                            ):  # replicate the torus crossover
                                if DEBUG and y < Ny:
                                    print(
                                        "v[{0}][{1}][{2}][{3}][{4}] = 1".format(
                                            x, y, c, p, t
                                        )
                                    )
                                drawn = True

                                if y == 0:
                                    canvas.create_line(
                                        self.get_v_channel_x(x, c, t),
                                        self.get_v_channel_y2(0, 0)
                                        + self.torus_loop_arc_vertical_box_height / 2,
                                        self.get_v_channel_x(x, c, t),
                                        self.get_v_channel_y2(y, c),
                                        fill="{0}".format(palette[p % len(palette)]),
                                        width=arrowWidth,
                                        arrow=tk.LAST,
                                        arrowshape=arrowshaper,
                                    )
                                elif y < Ny:
                                    canvas.create_line(
                                        self.get_v_channel_x(x, c, t),
                                        self.get_v_channel_y1(y, c),
                                        self.get_v_channel_x(x, c, t),
                                        self.get_v_channel_y2(y, c),
                                        fill="{0}".format(palette[p % len(palette)]),
                                        width=arrowWidth,
                                        arrow=tk.LAST,
                                        arrowshape=arrowshaper,
                                    )
                                elif y == Ny:  # vertical torus edge
                                    canvas.create_line(
                                        self.get_v_channel_x(x, c, t),
                                        self.get_v_channel_y1(y, c),
                                        self.get_v_channel_x(x, c, t),
                                        self.get_v_channel_y2(y, c)
                                        + self.torus_loop_arc_vertical_box_height / 2,
                                        fill="{0}".format(palette[p % len(palette)]),
                                        width=arrowWidth,
                                    )
                                    canvas.create_arc(
                                        self.get_v_channel_x(x, c, t),
                                        self.get_v_channel_y2(y, c)
                                        + self.torus_loop_arc_vertical_box_height,
                                        self.get_v_channel_x(x, 0, T - t - 1)
                                        + 1.5 * self.offsetx,
                                        self.get_v_channel_y2(y, c),
                                        start=0,
                                        extent=180,
                                        style="arc",
                                        outline="{0}".format(palette[p % len(palette)]),
                                        width=arrowWidth,
                                    )
                                    canvas.create_line(
                                        self.get_v_channel_x(x, 0, T - t - 1)
                                        + (1.5 * self.offsetx),
                                        self.get_v_channel_y2(y, c)
                                        + self.torus_loop_arc_vertical_box_height / 2,
                                        self.get_v_channel_x(x, 0, T - t - 1)
                                        + (1.5 * self.offsetx),
                                        self.get_v_channel_y2(0, 0)
                                        + self.torus_loop_arc_vertical_box_height / 2,
                                        fill="{0}".format(palette[p % len(palette)]),
                                        width=arrowWidth,
                                    )
                                    canvas.create_arc(
                                        self.get_v_channel_x(x, c, t),  # -50,
                                        self.get_v_channel_y2(0, 0)
                                        + self.torus_loop_arc_vertical_box_height,
                                        self.get_v_channel_x(x, 0, T - t - 1)
                                        + (1.5 * self.offsetx),
                                        # +self.torus_loop_arc_vertical_box_height,#self.get_v_channel_y2( 0, c )+(1+T-t)*self.offsety,
                                        self.get_v_channel_y2(0, 0),
                                        start=0,
                                        extent=-180,
                                        # width=2,
                                        style="arc",
                                        outline="{0}".format(palette[p % len(palette)]),
                                        width=arrowWidth,
                                    )
                        if not drawn:
                            # If unused in this cycle, draw a gray arrow
                            canvas.create_line(
                                self.get_v_channel_x(x, c, t),
                                self.get_v_channel_y1(y, c),
                                self.get_v_channel_x(x, c, t),
                                self.get_v_channel_y2(y, c),
                                fill="light gray",
                                width=4,
                                arrow=tk.LAST,
                                arrowshape=arrowshaper,
                            )
                        # if t==0:
                        #     # write a little '0' to indicate start cycle
                        #     canvas.create_text(
                        #         self.get_v_channel_x( x, c, t ),
                        #          self.get_v_channel_y1( y, c ) + (self.switch_image_height/10),
                        #         font=f'Times {int(2*ZOOM)}',
                        #         text='0')

        # (x,y) label outside of PE box
        for x in range(0, Nx):
            for y in range(0, Ny):
                canvas.create_text(
                    self.get_x1(x) + self.offsetx * 0.7,
                    self.get_y1(y) - self.offsety / 4,
                    font=f"Times {int(4 * ZOOM)}",
                    text="(" + str(x) + "," + str(y) + ") ",
                )
        x = 0
        y = 0
        canvas.create_text(
            self.get_x2(x) - 100,
            self.get_y2(y) - 20,
            text=f"CTX 0",
            font=f"Times {6 * ZOOM}",
            # fill="{}".format( color ))
        )
        canvas.create_text(
            self.get_x2(x) + 155,  # - self.x_reg_table_width/2,
            self.get_y2(y) - 20,  # - self.y_reg_table_height/2,
            # self.get_x1( x ) + self.x_reg_table_width,
            # self.get_exit_table_y2( y, t ),
            text=f"CTX 1",
            font=f"Times {6 * ZOOM}",
            # fill="{}".format( color ))
        )
        canvas.create_line(
            self.get_x2(x) - 38,
            self.get_y2(y) - 23,
            self.get_x2(x) + 19,
            self.get_y2(y) - 23,
            width=6,
            arrow=tk.LAST,
            arrowshape=arrowshaper,
            fill="black",
        )

        canvas.create_line(
            self.get_x2(x) + 95,
            self.get_y2(y) - 23,
            self.get_x2(x) + 38,
            self.get_y2(y) - 23,
            width=6,
            arrow=tk.LAST,
            arrowshape=arrowshaper,
            fill="black",
        )

        # SVG output
        if not os.path.exists("svg"):
            print("Creating 'svg' directory")
            os.makedirs("svg")

        if args.o == "":
            # import pd
            print("TODO OUTPUT PATH")
            # output_path = "svg/" + filename.split(".sol")[0].split("results/")[1] + ".svg"
            output_path = "svg/tmp.svg"
        canvasvg.saveall(output_path, canvas, items=None, margin=10, tounicode=None)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Torus GUI")
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()

# def visualize_schedule( dataflow_hypergraph, Nx, Ny, dfg_node_to_xy, output_path, kill=True ):
#     root = tk.Tk()
#     root.title("Placement Visualizer")
#     MainApplication(Nx, Ny, dataflow_hypergraph, dfg_node_to_xy, output_path, kill, root ).pack(side="top", fill="both", expand=True)
#     if kill:
#         root.quit()
#     else:
#         root.mainloop()
