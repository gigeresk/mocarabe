#define N 1024
void int_poly_quadratic(int x[N], int c[N], int y[N]) {
	loop1: for(int i=0; i<N; i++)
	{
		y[i] = (1 + x[i]*(5 + x[i]*c[i] ));
	}
}
