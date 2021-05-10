#define N 1024

void int_caprasse(int x[N], int y[N], int z[N], int t[N], int ret[N]) {
    for( int i=0; i < N; i++)
    {
	loop1: ret[i] = y[i]*y[i]*z[i] + 2*x[i]*y[i]*t[i] + 2*x[i] + z[i];
    }
}
