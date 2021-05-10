int int_level1_linear(int x1, int x2, int c1, int c2, int* ret)
{
	int T1 = x1 + x2 + c1;
	*ret =  c2*T1*T1;
}
