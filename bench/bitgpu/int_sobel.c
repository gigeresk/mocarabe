void int_sobel(int ul, // upper left
        int um, // upper middle
        int ur, // upper right
        int ml, // middle left
        int mr, // middle right
        int ll, // lower left
        int lm, // lower middle
        int lr, // lower right
        int fscale,
        int result
        )
{
        int T1 = ur + 2*mr + lr + ul + 2*ml + ll;
        int T2 = ul + 2*um + ur + ll + 2*lm + lr;
        result = fscale*(T1+T2);
}
