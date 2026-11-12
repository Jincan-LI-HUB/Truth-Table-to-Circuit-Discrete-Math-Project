#include <bits/stdc++.h>
#include "algebraic_mapper.hpp"
using namespace std;
int main(int argc,char**argv){if(argc<4)return 2;ifstream is(argv[1]);int n,m;is>>n>>m;
ifstream fs(argv[2]);string s((istreambuf_iterator<char>(fs)),{});int mode=argc>4?atoi(argv[4]):2;
string out=round4_algebra::rewrite(s,n,m,mode);if(out.empty())return 3;ofstream f(argv[3]);f<<out;
}
