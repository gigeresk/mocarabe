// Refer to Deriche Filter wikipedia.
// only consider one Channel.
void int_deriche(int x1,
            int x2,
            int x3,
            int x4,
            int x5,
            int x6,
            int x7,
            int x8,

            int y1,
            int y2,
            int y3,
            int y4,
            int y5,
            int y6,
            int y7,
            int y8,

            int z1,
            int z2,
            int z3,
            int z4,
            int z5,
            int z6,
            int z7,
            int z8,

            int w1,
            int w2,
            int w3,
            int w4,
            int w5,
            int w6,
            int w7,
            int w8,

            int h1,
            int h2,
            int h3,
            int h4,

            int c1,
            int c2,

            int a1,
            int a2,
            int a3,
            int a4,
            int a5,
            int a6,
            int a7,
            int a8,

            int b1,
            int b2,

            int *sum)
{
    int T0 = c1 * ( a1*x1 + a2*x2 + b1*y1 + b2*y2 + a3*x3 + a4*x4 + b1*y3 + b2*y4 );
    int T1 = c1 * ( a1*x5 + a2*x6 + b1*y5 + b2*y6 + a3*x7 + a4*x8 + b1*y7 + b2*y8 );
    int T2 = c1 * ( a1*z1 + a2*z2 + b1*w1 + b2*w2 + a3*z3 + a4*z4 + b1*w3 + b2*w4 );
    int T3 = c1 * ( a1*z5 + a2*z6 + b1*w5 + b2*w6 + a3*z7 + a4*z8 + b1*w7 + b2*w8 );

    int T4 = a5*T0 + a6*T1 + b1*h1 + b2*h2;
    int T5 = a7*T2 + a8*T3 + b1*h3 + b2*h4;
    *sum = c2*(T4 + T5);
}
