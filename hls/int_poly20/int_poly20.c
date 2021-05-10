#define N 1024
void int_poly20(int x[N], int c1[N], int c2[N], int c3[N], int c4[N], int c5[N], int c6[N], int c7[N], int c8[N], int c9[N],
        int a0[N], int a1[N], int a2[N], int a3[N], int a4[N], int a5[N], int a6[N], int a7[N], int a8[N], int a9[N], int y[N] )
{
        loop1: for(int i=0; i<N; i++)
	{
	y[i] =  x[i]*
        (c1[i] + x[i]*
         (c2[i] + x[i]*
          (c3[i] + x[i]*
           (c4[i] + x[i]*
            (c5[i] + x[i]*
             (c6[i] + x[i]*
              (c7[i] + x[i]*
               (c8[i] + x[i]*
                (c9[i] + x[i]*
                 (a0[i] + x[i]*
                  (a1[i] + x[i]*
                   (a2[i] + x[i]*
                    (a3[i] + x[i]*
                     (a4[i] + x[i]*
                       (a5[i] + x[i]*
                        (a6[i] + x[i]*
                         (a7[i] + x[i]*
                          (a8[i] + x[i]*
                           (a9[i] + x[i] )))))))))))))))))));
        }
}
