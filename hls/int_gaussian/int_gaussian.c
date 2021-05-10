#define N 1024
// I tried to write a complete Gaussian filter[], but we cannot support complex C program. I have to simplify it by pre-defining all the coefficients.
//
// Assume 3x3 pixels[], and only consider one channel of RGB.
void int_gaussian(int r0[N], int r1[N], int r2[N],
            int r3[N], int r4[N], int r5[N],
            int r6[N], int r7[N], int r8[N],
            int c0[N], int c1[N], int c2[N],
            int c3[N], int c4[N], int c5[N],
            int c6[N], int c7[N], int c8[N],
            int sum[N])
{
    loop1: for(int i=0; i<N; i++)
    {
        int T0 = r0[i]*c0[i];
        int T1 = r1[i]*c1[i];
        int T2 = r2[i]*c2[i];
        int T3 = r3[i]*c3[i];
        int T4 = r4[i]*c4[i];
        int T5 = r5[i]*c5[i];
        int T6 = r6[i]*c6[i];
        int T7 = r7[i]*c7[i];
        int T8 = r8[i]*c8[i];

        sum[i] = T0+T1+T2+T3+T4+T5+T6+T7+T8;
    }
}
