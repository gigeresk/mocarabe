int int_iir8(int a0,
	 int a1,
	 int a2,
	 int a3,
	 int a4,
	 int a5,
	 int a6,
	 int a7,
	 int b0,
	 int b1,
	 int b2,
	 int b3,
	 int b4,
	 int b5,
	 int b6,
	 int x0,
	 int x1,
	 int x2,
	 int x3,
	 int x4,
	 int x5,
	 int x6,
	 int x7,
	 int y0,
	 int y1,
	 int y2,
	 int y3,
	 int y4,
	 int y5,
	 int y6,
	 int y7
	 )
{
	y0 = a0*x0;
	y1 = a1*x1 + y0 - b0*y0;
	y2 = a2*x2 + y1 - b1*y1;
	y3 = a3*x3 + y2 - b2*y2;
	y4 = a4*x4 + y3 - b3*y3;
	y5 = a5*x5 + y4 - b4*y4;
	y6 = a6*x6 + y5 - b5*y5;
	y7 = a7*x7 + y6 - b6*y6;
}
