def generate_and_write_noc_mux_memories(rtl_dir, h, v, enter, exit_, Nx, Ny, C, P, T, noc_pipelining_stages):
    eastbound_mux_mem = verilog_eastbound_mux_mem_gen(
        h, v, enter, exit_, Nx, Ny, C, P, T, noc_pipelining_stages)
    for x in range(Nx):
        for y in range(Ny):
            for c in range(C):
                eastbound_mux_mem_str = print_mux_mem(
                    eastbound_mux_mem, x, y, c, T)
                filename = rtl_dir + f'noc_memory_e_x{x}_y{y}_c{c}.dat'

                file = open(filename, "w+")
                file.write(eastbound_mux_mem_str)
                file.close()

    northbound_mux_mem = verilog_northbound_mux_mem_gen(
        h, v, enter, exit_, Nx, Ny, C, P, T, noc_pipelining_stages)

    for x in range(Nx):
        for y in range(Ny):
            for c in range(C):
                northbound_mux_mem_str = print_mux_mem(
                    northbound_mux_mem, x, y, c, T)
                filename = rtl_dir + f'noc_memory_n_x{x}_y{y}_c{c}.dat'

                file = open(filename, "w+")
                file.write(northbound_mux_mem_str)
                file.close()

    pebound_mux_mem = verilog_pebound_mux_mem_gen(
        h, v, enter, exit_, Nx, Ny, C, P, T, noc_pipelining_stages)

    for x in range(Nx):
        for y in range(Ny):
            for c in range(C):
                pebound_mux_mem_str = print_mux_mem(
                    pebound_mux_mem, x, y, c, T)

                filename = rtl_dir + f'noc_memory_pe_x{x}_y{y}_c{c}.dat'
                file = open(filename, "w+")
                file.write(pebound_mux_mem_str)
                file.close()


def print_mux_mem(mux_mem, x, y, c, T):
    # shifting by 1, okay?  Only tested on II=2
    mux_mem_str = ""
    for t in range(T):
        mux_mem_str = mux_mem_str + mux_mem[x][y][c][t] + '\n'

    return mux_mem_str


def verilog_eastbound_mux_mem_gen(h, v, enter, exit_, Nx, Ny, C, P, T, noc_pipelining_stages):
    mem = [[[['11' for t in range(T)] for c in range(C)]
            for y in range(Ny)] for x in range(Nx)]
    for x in range(Nx):
        for y in range(Ny):
            for c in range(C):
                # for every mux, initialize and iterate through 'v'
                # for every v == 1, for that channel, look back
                for t in range(T):
                    for p in range(P):
                        if h[x][y][c][p][t] == 1:
                            # mux fires at (t - noc_pipelining_stages) % T to account for
                            # the i_from_pe_reg 1-cycle delay in torus_switch
                            mux_slot = (t - noc_pipelining_stages) % T
                            # find source...
                            if v[(x-1) % Nx][y][c][p][(t-noc_pipelining_stages-1) % T] == 1:
                                mem[(x-1) % Nx][y][c][mux_slot] = "00"
                            elif h[(x-1) % Nx][y][c][p][(t-noc_pipelining_stages-1) % T] == 1:
                                mem[(x-1) % Nx][y][c][mux_slot] = "01"
                            elif enter[(x-1) % Nx][y][c][p][(t-noc_pipelining_stages-1) % T] == 1:
                                mem[(x-1) % Nx][y][c][mux_slot] = "10"
                            else:
                                raise AssertionError(
                                    "An eastbound mux is in an impossible state (does noc pipeling match with scheduler state?)")
    return mem


def verilog_northbound_mux_mem_gen(h, v, enter, exit_, Nx, Ny, C, P, T, noc_pipelining_stages):
    mem = [[[['11' for t in range(T)] for c in range(C)]
            for y in range(Ny)] for x in range(Nx)]

    for x in range(Nx):
        for y in range(Ny):
            for c in range(C):
                # for every mux, initialize and iterate through 'h'
                # for every h == 1, for that channel, look back
                for t in range(T):
                    for p in range(P):
                        if v[x][y][c][p][t] == 1:
                            # mux fires at (t - noc_pipelining_stages) % T to account for
                            # the i_from_pe_reg 1-cycle delay in torus_switch
                            mux_slot = (t - noc_pipelining_stages) % T
                            # find source...
                            if v[x][(y-1) % Ny][c][p][(t-noc_pipelining_stages-1) % T] == 1:
                                mem[x][(y-1) % Ny][c][mux_slot] = "00"
                            elif h[x][(y-1) % Ny][c][p][(t-noc_pipelining_stages-1) % T] == 1:
                                mem[x][(y-1) % Ny][c][mux_slot] = "01"
                            elif enter[x][(y-1) % Ny][c][p][(t-noc_pipelining_stages-1) % T] == 1:
                                mem[x][(y-1) % Ny][c][mux_slot] = "10"
                            else:
                                raise AssertionError(
                                    "A northbound mux is in an impossible state (does noc pipeling match with scheduler state?)")
    return mem


def verilog_pebound_mux_mem_gen(h, v, enter, exit_, Nx, Ny, C, P, T, noc_pipelining_stages):
    mem = [[[['11' for t in range(T)] for c in range(C)]
            for y in range(Ny)] for x in range(Nx)]
    for x in range(Nx):
        for y in range(Ny):
            for c in range(C):
                # for every mux, initialize and iterate through 'h'
                # for every h == 1, for that channel, look back
                for t in range(T):
                    for p in range(P):
                        if exit_[x][y][c][p][t] == 1:
                            # mux fires at (t - noc_pipelining_stages) % T to account for
                            # the i_from_pe_reg 1-cycle delay in torus_switch
                            mux_slot = (t - noc_pipelining_stages) % T
                            # find source...
                            if v[x][y][c][p][(t-noc_pipelining_stages-1) % T] == 1:
                                mem[x][y][c][mux_slot] = "00"
                            elif h[x][y][c][p][(t-noc_pipelining_stages-1) % T] == 1:
                                mem[x][y][c][mux_slot] = "01"
                            elif enter[x][y][c][p][(t-noc_pipelining_stages-1) % T] == 1:
                                mem[x][y][c][mux_slot] = "10"
                            else:
                                raise AssertionError(
                                    "A pebound mux is in an impossible state (does noc pipeling match with scheduler state?)")
    return mem
