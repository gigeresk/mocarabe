#define N 1024

void int_fir32(
        int x0[N], int a0[N],
        int x1[N], int a1[N],
        int x2[N], int a2[N],
        int x3[N], int a3[N],
        int x4[N], int a4[N],
        int x5[N], int a5[N],
        int x6[N], int a6[N],
        int x7[N], int a7[N],
        int x8[N], int a8[N],
        int x9[N], int a9[N],
        int y0[N], int b0[N],
        int y1[N], int b1[N],
        int y2[N], int b2[N],
        int y3[N], int b3[N],
        int y4[N], int b4[N],
        int y5[N], int b5[N],
        int y6[N], int b6[N],
        int y7[N], int b7[N],
        int y8[N], int b8[N],
        int y9[N], int b9[N],
        int z0[N], int c0[N],
        int z1[N], int c1[N],
        int z2[N], int c2[N],
        int z3[N], int c3[N],
        int z4[N], int c4[N],
        int z5[N], int c5[N],
        int z6[N], int c6[N],
        int z7[N], int c7[N],
        int z8[N], int c8[N],
        int z9[N], int c9[N],
        int w0[N], int d0[N],
        int w1[N], int d1[N],
        int w2[N], int d2[N],
        int ret[N]
        )
{
        loop1: for(int i=0; i<N; i++)
        {
	*ret =  x0[i]*a0[i] + x1[i]*a1[i] + x2[i]*a2[i] + x3[i]*a3[i] + x4[i]*a4[i] + x5[i]*a5[i] + x6[i]*a6[i] + x7[i]*a7[i] + x8[i]*a8[i] + x9[i]*a9[i] +
        y0[i]*b0[i] + y1[i]*b1[i] + y2[i]*b2[i] + y3[i]*b3[i] + y4[i]*b4[i] + y5[i]*b5[i] + y6[i]*b6[i] + y7[i]*b7[i] + y8[i]*b8[i] + y9[i]*b9[i] +
        z0[i]*c0[i] + z1[i]*c1[i] + z2[i]*c2[i] + z3[i]*c3[i] + z4[i]*c4[i] + z5[i]*c5[i] + z6[i]*c6[i] + z7[i]*c7[i] + z8[i]*c8[i] + z9[i]*c9[i] +
        w0[i]*d0[i] + w1[i]*d1[i] + w2[i]*d2[i];
        }
}
