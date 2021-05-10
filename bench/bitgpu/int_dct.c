void int_dct(int x0, int x1, int x2, int x3, int x4, int x5, int x6, int x7,
        int a, int b, int c, int d, int e, int f, int g,
        int* y0, int* y1, int* y2, int* y3, int* y4, int* y5, int* y6, int* y7)
{
    int T1 = x0+x7;
    int T2 = x1+x6;
    int T3 = x2+x5;
    int T4 = x3+x4;
    int T5 = x0+x7;
    int T6 = x1+x6;
    int T7 = x2+x5;
    int T8 = x3+x4;

    *y0 = (T1+T2+T3+T4)*g;
    *y2 = b*(T1+T4) + e*(T2+T3);
    *y4 = ((T1+T4) + (T2+T3))*g;
    *y6 = e*(T1+T4) + b*(T2+T3);

    *y1 = a*T5 + c*T6 + d*T7 + f*T8;
    *y3 = c*T5 + f*T6 + a*T7 + d*T8;
    *y5 = d*T5 + a*T6 + f*T7 + c*T8;
    *y7 = f*T5 + d*T6 + c*T7 + a*T8;
}
