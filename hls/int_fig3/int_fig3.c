#define N 1024

int int_fig3(int a[N], int b[N], int c[N], int ret[N])
{
    loop1: for(int i = 0; i < N; i++)
    {
        ret[i] = a[i]*b[i] + c[i] + b[i];
    }
}

