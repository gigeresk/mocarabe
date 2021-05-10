#define N 1
int int_level1_saturation(int x1, //vd
        int x2, //vg
        int x3, //vs
        int c1, //vt
        int c2,
        int ret) //b
{
        ret = c2*(x2+x3+c1+(x1+x3)*5)*(x1+x3);
}

