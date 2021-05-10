#define N 1024

void int_level1_linear(int x1[N], int x2[N], int c1[N], int c2[N], int ret[N])
{
	loop1: for(int i=0; i<N; i++)
	{
		int T1 = x1[i] + x2[i] + c1[i];
		ret[i] = c2[i]*T1*T1;
	}
}
