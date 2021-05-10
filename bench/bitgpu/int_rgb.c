//void rgb(unsigned int R, unsigned int G, unsigned int B,
void int_rgb(int R, int G, int B,
        int c1, int c2, int c3,
        int c4, int c5, int c6,
        int c7,
        int c8, int c9,
        int Y, int Cb, int Cr)
    {
    Y =  c1*R + c2*G + c3*B;
    Cb = c4*R + c5*G + c6*B;
    Cr = c7*R + c8*G + c9*B;
}
