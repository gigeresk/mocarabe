#define N 1024
void int_rgb(int R[N], int G[N], int B[N],
        int c1[N], int c2[N],  int c3[N],
        int c4[N], int c5[N], int c6[N],
        int c7[N],
        int c8[N], int c9[N],
        int Y[N], int Cb[N], int Cr[N])
    {
loop1:
for (int i=0; i < N; i++) {
    Y[i] =  c1[i]*R[i] + c2[i]*G[i] + c3[i]*B[i];
    Cb[i] = c4[i]*R[i] + c5[i]*G[i] + c6[i]*B[i];
    Cr[i] = c7[i]*R[i] + c8[i]*G[i] + c9[i]*B[i];
}
}
