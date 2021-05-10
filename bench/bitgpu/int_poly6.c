int int_poly6(int x, int c1, int c2, int c3, int* y)
{
	*y = x*(1 + x*(5 + x*(c1 + x*(25 + x*(c2 + x*c3)))));
}
