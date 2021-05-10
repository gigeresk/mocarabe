#define N 1024

void int_poly10(int x[N], int c1[N], int c2[N], int c3[N], int c4[N], int c5[N], int c6[N], int y[N]) {
 	loop1:	for(int i=0; i<N; i++)
	{
		y[i] = x[i]*(1 + x[i]*(5 + x[i]*(c1[i] + x[i]*(25 + x[i]*(c2[i] + x[i]*(c3[i] + x[i]*(c4[i] + x[i]*(125 + x[i]*(c5[i] + x[i]*c6[i])))))))));
	}
}
