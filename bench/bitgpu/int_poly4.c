int int_poly4(int x, int c, int* y) {
	*y = x*(1 + x*(5 + x*(c + x*25)));
}
