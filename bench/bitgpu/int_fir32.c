int int_fir32(
        int x0, int a0,
        int x1, int a1,
        int x2, int a2,
        int x3, int a3,
        int x4, int a4,
        int x5, int a5,
        int x6, int a6,
        int x7, int a7,
        int x8, int a8,
        int x9, int a9,
        int y0, int b0,
        int y1, int b1,
        int y2, int b2,
        int y3, int b3,
        int y4, int b4,
        int y5, int b5,
        int y6, int b6,
        int y7, int b7,
        int y8, int b8,
        int y9, int b9,
        int z0, int c0,
        int z1, int c1,
        int z2, int c2,
        int z3, int c3,
        int z4, int c4,
        int z5, int c5,
        int z6, int c6,
        int z7, int c7,
        int z8, int c8,
        int z9, int c9,
        int w0, int d0,
        int w1, int d1,
        int w2, int d2,
        int* ret
        )
{
	*ret =  x0*a0 + x1*a1 + x2*a2 + x3*a3 + x4*a4 + x5*a5 + x6*a6 + x7*a7 + x8*a8 + x9*a9 +
        y0*b0 + y1*b1 + y2*b2 + y3*b3 + y4*b4 + y5*b5 + y6*b6 + y7*b7 + y8*b8 + y9*b9 +
        z0*c0 + z1*c1 + z2*c2 + z3*c3 + z4*c4 + z5*c5 + z6*c6 + z7*c7 + z8*c8 + z9*c9 +
        w0*d0 + w1*d1 + w2*d2;
}
