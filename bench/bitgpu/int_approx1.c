int int_approx1(int x1, int x2, int x3, int c1, int c2, int* y)
{
    // vg:x1, vs:x2, vd:x3
    int T1 = x1 + c1;
    int T2 = T1 + x2;
    int T3 = T1 + x3;
    *y = c2*(T2*T2 + T3*T3);
}

