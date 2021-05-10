# # -*- coding: future_fstrings -*-
# add more colours/richer colour logic
# draw full path
# take into account  when enter and exit occurs at the same time

import os
import tkinter as tk
import sys
import re
import argparse
import json
import ast
import numpy as np
import random
import time

try:
    import pyscreenshot as ImageGrab
    from PIL import ImageTk, Image #might need to do sudo apt-get install python3-pil.imagetk
except:
    print( "I think you might have to do a little $sudo apt-get install python3-pil.imagetk")
try:
    import canvasvg
except:
    print("pip3 install canvasvg")
try:
    import palettable
except:
    print("pip3 install palettable")

# TIME = 0 #global, current frame time
# parser = argparse.ArgumentParser(description='GUI for cgra-ilp. This version has no time cycling')
# parser.add_argument('-sched',  type=str, required=True, help='sol file for the GUI to visualize')
# parser.add_argument('--zoom', type=int, default=2, help='magnify everything in the GUI, except for the arrows')
# parser.add_argument('--net', type=str, required=True, help='Netlist for labelling operators, etc. ')
# parser.add_argument('-o', type=str, default="", help='export SVG path ') #TODO

DEBUG = False
ZOOM = 2
#https://jiffyclub.github.io/palettable/colorbrewer/
# change the palette here
palette = palettable.tableau.Tableau_20.hex_colors

class MainApplication(tk.Frame):

    def get_x1( self, x ):
        return self.stepx*(x) + self.offsetx

    def get_x2( self, x ):
        return self.stepx*(x+1)

    def get_y1( self, y ):
        return self.MAXHEIGHT-(self.stepy*(y+1)+self.offsety)

    def get_y2( self, y ):
        return self.MAXHEIGHT-(self.stepy*(y+2))


    def __init__(self, Nx, Ny, dataflow_hypergraph, dfg_node_to_xy, output_path, energy=0, kill=True, parent=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        # args = parser.parse_args()

        # filename = args.sched
        # ZOOM = args.zoom
        # serialized_labels = args.labels

        # netlist_filename = args.net
        # print("filename:",filename)
        # assert( os.path.exists( filename ) ), f"Schedule path {filename} does not exist"
        # assert( os.path.exists( netlist_filename ) ), f"Netlist path {netlist_filename} does not exist"
        # assert( os.path.exists( serialized_labels ) ), f"Label path {serialized_labels} does not exist"
        # assert( os.path.exists( output_path ) ), f"Output path {output_path} does not exist"


        # first, get labels and ops ready

        # pixel counting
        base_stepx  = 70
        base_stepy = 70
        base_offsetx = 20
        base_offsety = 20
        self.stepx= base_stepx * ZOOM
        self.stepy= base_stepy * ZOOM
        self.offsetx= base_offsetx * ZOOM
        self.offsety= base_offsety * ZOOM
        #todo get rid of
        offsetx= base_offsetx * ZOOM
        offsety= base_offsety * ZOOM

        frame=tk.Frame(self)
        frame.config(bg='yellow')
        frame.pack()

        self.MAXHEIGHT=(Ny+1)*self.stepy+offsety
        canvas = tk.Canvas(self, width=Nx*self.stepx+3*offsetx, height=(Ny)*self.stepy+3*offsetx)
        self._canvas = canvas
        canvas.pack()
        canvas.configure(background='black')

        #Scrollbar (Ctrl + mousewheel to scroll horizontally)
        vbar=tk.Scrollbar(frame,orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT,fill=tk.Y)

        canvas.bind('<4>', lambda event : canvas.yview('scroll', -1, 'units'))
        canvas.bind('<5>', lambda event : canvas.yview('scroll', 1, 'units'))
        canvas.bind('<Control-4>', lambda event : canvas.xview('scroll', -1, 'units'))
        canvas.bind('<Control-5>', lambda event : canvas.xview('scroll', 1, 'units'))
    
        canvas.create_rectangle( 0, 0, Nx*self.stepx+3*offsetx, (Ny)*self.stepy+3*offsetx, fill="white" )
        if energy != 0:
            canvas.create_text( (Nx*self.stepx+3*offsetx)//2, 20, text=str(energy) )
        #PE box at every (x,y)
        for x in range(0,Nx):
            for y in range(0,Ny):
                # PE box
                canvas.create_rectangle(
                    self.get_x1( x ),
                    self.get_y1( y ),
                    self.get_x2( x ),
                    self.get_y2( y )
                )

        # (x,y) label outside of PE box
        for x in range(0,Nx):
            for y in range(0,Ny):
                canvas.create_text(
                    self.get_x2( x ) + self.offsetx/10,
                    self.get_y2( y ) - self.offsety/10,
                    text=str(x)+","+str(y)
                )

        # dataflow graph
        num_of_nets = len( dataflow_hypergraph.ordered_hyperedge_id_list() )
        p=0
        for h_edge_id in dataflow_hypergraph.ordered_hyperedge_id_iterator():

            hyperedge = dataflow_hypergraph.get_hyperedge_attributes( h_edge_id )

            assert( len( hyperedge['tail'] ) <= 1 ), "DFG hyperedges can only have one source ('tail' attribute)"
            src = hyperedge['tail'][0]
            sinks = hyperedge['head']

            offset = (p/num_of_nets)* (self.stepx-self.offsetx)

            src_pe = dfg_node_to_xy[int(src)]
            
            canvas.create_text(
                self.get_x1( src_pe[0] ) + random.randint(0,base_offsetx),
                self.get_y1( src_pe[1] ) - random.randint(0,base_offsety),
                font=f"Times 12",
                text=dataflow_hypergraph.get_node_attribute(src,'label'),
                fill=palette[p % len( palette )]
            )
            for sink in sinks:
                if int(sink) in dfg_node_to_xy:
                    sink_pe = dfg_node_to_xy[int(sink)]

                    if sink_pe[0] >= src_pe[0] and sink_pe[1] >= src_pe[1]:
                        # dominate

                        if src_pe[1] == sink_pe[1]:
                            canvas.create_line(
                                self.get_x1( src_pe[0] ) + offset,
                                self.get_y1( src_pe[1] ) - offset,
                                self.get_x1( sink_pe[0] ) + offset,
                                self.get_y1( sink_pe[1] ) - offset,
                                width=2,
                                arrow=tk.LAST,
                                fill="{}".format( palette[p % len( palette )])
                            )
                        else:
                            canvas.create_image(
                                self.get_x1( src_pe[0] ) + offset,
                                self.get_y1( src_pe[1] ) - offset,
                                #XY
                                self.get_x1( sink_pe[0] ) + offset,
                                self.get_y1( src_pe[1] ) - offset,

                                self.get_x1( sink_pe[0] ) + offset,
                                self.get_y1( sink_pe[1] ) - offset,
                                width=2,
                                # arrow=tk.LAST,
                                # stipple="gray50",
                                fill="{}".format( palette[p % len( palette )])
                            )
                    elif sink_pe[0] >= src_pe[0] and sink_pe[1] < src_pe[1]:
                        # rollover North only
                        # Northwards
                        # X
                        canvas.create_line(
                            self.get_x1( src_pe[0] ) + offset,
                            self.get_y1( src_pe[1] ) - offset,
                            self.get_x1( sink_pe[0] ) + offset,
                            self.get_y1( src_pe[1] ) - offset,
                            width=2,
                            fill="{}".format( palette[p % len( palette )])
                        )
                        canvas.create_line(
                            self.get_x1( sink_pe[0] ) + offset,
                            self.get_y1( src_pe[1] ) - offset,
                            self.get_x1( sink_pe[0] ) + offset,
                            self.get_y1( Ny) - offset,
                            width=2,
                            fill="{}".format( palette[p % len( palette )])
                        )
                        # Y
                        canvas.create_line(
                            self.get_x1( sink_pe[0] ) + offset,
                            self.get_y1( 0 ) - offset,
                            self.get_x1( sink_pe[0] ) + offset,
                            self.get_y1( sink_pe[1] ) - offset,
                            width=2,
                            arrow=tk.LAST,
                            fill="{}".format( palette[p % len( palette )])
                        )
                    elif sink_pe[0] < src_pe[0] and sink_pe[1] >= src_pe[1]:
                        # rollover East
                        # X
                        canvas.create_line(
                            self.get_x1( src_pe[0] ),
                            self.get_y1( src_pe[1] ) - offset,
                            self.get_x1( Nx ),
                            self.get_y1( src_pe[1] ) - offset,
                            width=2,
                            arrow=tk.LAST,
                            fill="{}".format( palette[p % len( palette )])
                        )
                        # Y
                        if src_pe[1] == sink_pe[1]:
                            canvas.create_line(
                                self.get_x1( 0 ),
                                self.get_y1( src_pe[1] ) - offset,
                                self.get_x1( sink_pe[0] ) + offset,
                                self.get_y1( sink_pe[1] ) - offset,
                                width=2,
                                arrow=tk.LAST,
                                fill="{}".format( palette[p % len( palette )])
                            )
                        else:
                            canvas.create_line(
                                self.get_x1( 0 ),
                                self.get_y1( src_pe[1] ) - offset,
                                self.get_x1( sink_pe[0] ) + offset,
                                self.get_y1( src_pe[1] ) - offset,
                                width=2,
                                fill="{}".format( palette[p % len( palette )])
                            )
                            canvas.create_line(
                                self.get_x1( sink_pe[0] ) + offset,
                                self.get_y1( src_pe[1] ) - offset,
                                self.get_x1( sink_pe[0] ) + offset,
                                self.get_y1( sink_pe[1] ) - offset,
                                width=2,
                                arrow=tk.LAST,
                                fill="{}".format( palette[p % len( palette )])
                            )
                    else:
                        # X 
                        canvas.create_line(
                            self.get_x1( src_pe[0] ),
                            self.get_y1( src_pe[1] ) - offset,
                            self.get_x1( Nx ),
                            self.get_y1( src_pe[1] ) - offset,
                            width=2,
                            arrow=tk.LAST,
                            fill="{}".format( palette[p % len( palette )])
                        )
                        # XY
                        canvas.create_line(
                            self.get_x1( 0 ),
                            self.get_y1( src_pe[1] ) - offset,
                            self.get_x1( sink_pe[0] ) + offset,
                            self.get_y1( src_pe[1] ) - offset,
                            width=2,
                            fill="{}".format( palette[p % len( palette )])
                        )
                        canvas.create_line(
                            self.get_x1( sink_pe[0] ) + offset,
                            self.get_y1( src_pe[1] ) - offset,
                            self.get_x1( sink_pe[0] ) + offset,
                            self.get_y1( Ny ),
                            width=2,
                            arrow=tk.LAST,
                            fill="{}".format( palette[p % len( palette )])
                        )
                        # Y
                        canvas.create_line(
                            self.get_x1( sink_pe[0] ) + offset,
                            self.get_y1( 0 ),
                            self.get_x1( sink_pe[0] ) + offset,
                            self.get_y1( sink_pe[1] ),
                            width=2,
                            arrow=tk.LAST,
                            fill="{}".format( palette[p % len( palette )])
                        )
                    canvas.create_text(
                        self.get_x1( sink_pe[0] ) + offset,
                        self.get_y1( sink_pe[1] ) - offset,
                        font=f"Times 12",
                        fill=palette[p % len( palette )],
                        text=dataflow_hypergraph.get_node_attribute(sink,'label')
                    )
            p=p+1

        if output_path == "":
            output_path = "svg/placement.svg"
      
        canvasvg.saveall(output_path, canvas, items=None, margin=10, tounicode=None)

        time.sleep(0.5)
        return


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Placement Visualizer")
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()


def visualize_placement( dataflow_hypergraph, Nx, Ny, dfg_node_to_xy, output_path, energy=0, kill=True ):
    root = tk.Tk()
    root.title("Placement Visualizer")
    root.configure(background='black')
    MainApplication(Nx, Ny, dataflow_hypergraph, dfg_node_to_xy, output_path, energy, kill, root ).pack(side="top", fill="both", expand=True)
    if kill:
        root.quit()
    else:
        root.mainloop()
