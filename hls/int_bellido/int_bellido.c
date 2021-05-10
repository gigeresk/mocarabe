#define N 1024

int int_bellido(int z1[N], int z2[N], int z3[N], int ret[N]) {
	loop1: for (int i=0; i < N; i++) {
		ret[i] = (z1[i]+6)*(z1[i]+6) + z2[i]*z2[i] + z3[i]*z3[i] + 104;
	}
}
