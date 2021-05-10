int int_poly(int x, int c, int* y) {
	*y =  x*(1 + x*(5 + x*(c + x*25)));
}
