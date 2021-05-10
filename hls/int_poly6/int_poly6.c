#define N 1024

int int_poly6(int x[N], int c1[N], int c2[N], int c3[N], int y[N])
{
	loop1: for(int i=0; i<N; i++)
	{
		y[i] = x[i]*(1 + x[i]*(5 + x[i]*(c1[i] + x[i]*(25 + x[i]*(c2[i] + x[i]*c3[i])))));
	}
}
