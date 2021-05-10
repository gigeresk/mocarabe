#define N 1024

void int_adder_chain(int x[N], int y[N], int z[N], int a[N],int ret[N] ) {

	loop1: for (int i=0; i < N; i++) {
		ret[i] = x[i]+y[i]+z[i]+a[i];
	}
}
