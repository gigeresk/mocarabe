#define N 1024
// Refer to Deriche Filter wikipedia.
// only consider one Channel.
void int_deriche(int x1[N],
            int x2[N],
            int x3[N],
            int x4[N],
            int x5[N],
            int x6[N],
            int x7[N],
            int x8[N],

            int y1[N],
            int y2[N],
            int y3[N],
            int y4[N],
            int y5[N],
            int y6[N],
            int y7[N],
            int y8[N],

            int z1[N],
            int z2[N],
            int z3[N],
            int z4[N],
            int z5[N],
            int z6[N],
            int z7[N],
            int z8[N],

            int w1[N],
            int w2[N],
            int w3[N],
            int w4[N],
            int w5[N],
            int w6[N],
            int w7[N],
            int w8[N],

            int h1[N],
            int h2[N],
            int h3[N],
            int h4[N],

            int c1[N],
            int c2[N],

            int a1[N],
            int a2[N],
            int a3[N],
            int a4[N],
            int a5[N],
            int a6[N],
            int a7[N],
            int a8[N],

            int b1[N],
            int b2[N],

            int sum[N])
{
    loop1: for(int i = 0; i < N; i++)
    {
        int T0 = c1[i] * ( a1[i]*x1[i] + a2[i]*x2[i] + b1[i]*y1[i] + b2[i]*y2[i] + a3[i]*x3[i] + a4[i]*x4[i] + b1[i]*y3[i] + b2[i]*y4[i] );
        int T1 = c1[i] * ( a1[i]*x5[i] + a2[i]*x6[i] + b1[i]*y5[i] + b2[i]*y6[i] + a3[i]*x7[i] + a4[i]*x8[i] + b1[i]*y7[i] + b2[i]*y8[i] );
        int T2 = c1[i] * ( a1[i]*z1[i] + a2[i]*z2[i] + b1[i]*w1[i] + b2[i]*w2[i] + a3[i]*z3[i] + a4[i]*z4[i] + b1[i]*w3[i] + b2[i]*w4[i] );
        int T3 = c1[i] * ( a1[i]*z5[i] + a2[i]*z6[i] + b1[i]*w5[i] + b2[i]*w6[i] + a3[i]*z7[i] + a4[i]*z8[i] + b1[i]*w7[i] + b2[i]*w8[i] );

        int T4 = a5[i]*T0 + a6[i]*T1 + b1[i]*h1[i] + b2[i]*h2[i];
        int T5 = a7[i]*T2 + a8[i]*T3 + b1[i]*h3[i] + b2[i]*h4[i];
        sum[i] = c2[i]*(T4 + T5); // return
    }
}
