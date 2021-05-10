#define N 1024
void int_dct(int x0[N], int x1[N], int x2[N], int x3[N], int x4[N], int x5[N], int x6[N], int x7[N],
        int a[N], int b[N], int c[N], int d[N], int e[N], int f[N], int g[N],
        int y0[N], int y1[N], int y2[N], int y3[N], int y4[N], int y5[N], int y6[N], int y7[N])
{
    loop1: for(int i=0; i<N; i++)
    {
        int T1 = x0[i]+x7[i];
        int T2 = x1[i]+x6[i];
        int T3 = x2[i]+x5[i];
        int T4 = x3[i]+x4[i];
        int T5 = x0[i]+x7[i];
        int T6 = x1[i]+x6[i];
        int T7 = x2[i]+x5[i];
        int T8 = x3[i]+x4[i];

        y0[i] = (T1+T2+T3+T4)*g[i];
        y2[i] = b[i]*(T1+T4) + e[i]*(T2+T3);
        y4[i] = ((T1+T4) + (T2+T3))*g[i];
        y6[i] = e[i]*(T1+T4) + b[i]*(T2+T3);

        y1[i] = a[i]*T5 + c[i]*T6 + d[i]*T7 + f[i]*T8;
        y3[i] = c[i]*T5 + f[i]*T6 + a[i]*T7 + d[i]*T8;
        y5[i] = d[i]*T5 + a[i]*T6 + f[i]*T7 + c[i]*T8;
        y7[i] = f[i]*T5 + d[i]*T6 + c[i]*T7 + a[i]*T8;
    }
}
