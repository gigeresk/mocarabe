#define N 1024

void int_approx1(int x1[N], int x2[N], int x3[N], int c1[N], int c2[N], int ret[N])
{
    // vg:x1, vs:x2, vd:x3
    int T1;
    int T2;
    int T3;
    loop1: for( int i=0; i<N; i++)
    {
        T1 = x1[i] + c1[i];
        T2 = T1 + x2[i];
        T3 = T1 + x3[i];
        ret[i] = c2[i]*((T2*T2) + (T3*T3));
    }
}

