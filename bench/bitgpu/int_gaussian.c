void int_gaussian(int r0, int r1, int r2,
            int r3, int r4, int r5,
            int r6, int r7, int r8,
            int c0, int c1, int c2,
            int c3, int c4, int c5,
            int c6, int c7, int c8,
            int *sum)
{
    int T0 = r0*c0;
    int T1 = r1*c1;
    int T2 = r2*c2;
    int T3 = r3*c3;
    int T4 = r4*c4;
    int T5 = r5*c5;
    int T6 = r6*c6;
    int T7 = r7*c7;
    int T8 = r8*c8;

    *sum = T0+T1+T2+T3+T4+T5+T6+T7+T8;
}
