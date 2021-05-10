#define N 1024
void int_sobel(int ul[N], // upper left
        int um[N], // upper middle
        int ur[N], // upper right
        int ml[N], // middle left
        int mr[N], // middle right
        int ll[N], // lower left
        int lm[N], // lower middle
        int lr[N], // lower right
        int fscale[N],
        int result[N]
        )
{
	loop1: for(int i = 0; i < N; ++i)
	{
                int T1 = ur[i] + 2*mr[i] + lr[i] + ul[i] + 2*ml[i] + ll[i];
                int T2 = ul[i] + 2*um[i] + ur[i] + ll[i] + 2*lm[i] + lr[i];
                result[i] = fscale[i]*(T1+T2);
	}
}
