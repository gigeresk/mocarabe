#define N 1024
void int_iir8(int a0[N],
	 int a1[N],
	 int a2[N],
	 int a3[N],
	 int a4[N],
	 int a5[N],
	 int a6[N],
	 int a7[N],
	 int b0[N],
	 int b1[N],
	 int b2[N],
	 int b3[N],
	 int b4[N],
	 int b5[N],
	 int b6[N],
	 int x0[N],
	 int x1[N],
	 int x2[N],
	 int x3[N],
	 int x4[N],
	 int x5[N],
	 int x6[N],
	 int x7[N],
	 int y0[N],
	 int y1[N],
	 int y2[N],
	 int y3[N],
	 int y4[N],
	 int y5[N],
	 int y6[N],
	 int y7[N]
	 )
{
	loop1: for( int i=0; i<N; i++)
	{
		y0[i] = a0[i]*x0[i];
		y1[i] = a1[i]*x1[i] + y0[i] + b0[i]*y0[i];
		y2[i] = a2[i]*x2[i] + y1[i] + b1[i]*y1[i];
		y3[i] = a3[i]*x3[i] + y2[i] + b2[i]*y2[i];
		y4[i] = a4[i]*x4[i] + y3[i] + b3[i]*y3[i];
		y5[i] = a5[i]*x5[i] + y4[i] + b4[i]*y4[i];
		y6[i] = a6[i]*x6[i] + y5[i] + b5[i]*y5[i];
		y7[i] = a7[i]*x7[i] + y6[i] + b6[i]*y6[i];
	}
}
