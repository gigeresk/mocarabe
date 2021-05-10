#define N 1024
int int_level1_saturation(int x1[N], //vd
        int x2[N], //vg
        int x3[N], //vs
        int c1[N], //vt
        int c2[N],
        int ret[N]) //b
{
    loop1: for(int i=0; i<N; i++)
    {
        ret[i] = c2[i]*(x2[i]+x3[i]+c1[i]+(x1[i]+x3[i])*5)*(x1[i]+x3[i]);
    }
}

