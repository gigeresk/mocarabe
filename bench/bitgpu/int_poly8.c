int int_poly8(int x, int c1, int c2, int c3, int c4, int y) {
	y = x*(1 + x*(5 + x*(c1 + x*(25 + x*(c2 + x*(c3 + x*(c4 + x*125 )))))));
}
