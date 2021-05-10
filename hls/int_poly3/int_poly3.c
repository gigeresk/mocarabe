#define N 1024
void int_poly3(int x[N], int a[N], int b[N], int c[N], int y[N]) {
	loop1: for(int i = 0; i < N; ++i)
	{
		y[i] = x[i]*(x[i]*(a[i] + (b[i]*x[i])) + c[i]);

	}
}
