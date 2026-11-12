#include <bits/stdc++.h>
#include <unistd.h>
#include <sys/wait.h>
using namespace std;
struct Score{bool valid=false;long long area=0;int delay=0;};
Score evaluate(const string &p,int n,int m,int aa,int da,int ao,int dor,int an,int dn){
 ifstream f(p);if(!f)return {};
 vector<int> ready(n+1,0);long long area=0;string line;int count=0;Score result;
 while(getline(f,line)){
  istringstream in(line);string first,type; if(!(in>>first))continue;
  int id;try{id=stoi(first);}catch(...){return {};}
  if(in>>type){int a,b=0;if(!(in>>a))return {};if(type!="NOT"&&!(in>>b))return {};
    if(id!=n+1+count||a<0||a>=id||b<0||b>=id)return {};
    if(type=="NOT"){ready.push_back(ready[a]+dn);area+=an;}
    else if(type=="AND2"){ready.push_back(max(ready[a],ready[b])+da);area+=aa;}
    else if(type=="OR2"){ready.push_back(max(ready[a],ready[b])+dor);area+=ao;}
    else return {};
    ++count;
  }else { // final line could have >1 outputs: parse ID plus remainder directly
    // reinterpret entire line as integer signal list
    istringstream o(line);vector<int> outs;int x;
    while(o>>x)outs.push_back(x);
    if((int)outs.size()!=m)return {};
    int d=0;for(int v:outs){if(v<0||v>=(int)ready.size())return {};d=max(d,ready[v]);}
    string extra;while(getline(f,extra))if(extra.find_first_not_of(" \t\r\n")!=string::npos)return {};
    return {true,area,d};
  }
 }
 return result;
}
// The parser above handles lines with two integers as final outputs via a type token check:
// a non-gate token on the final line needs a separate parse.
Score evalFile(const string&p,int n,int m,int aa,int da,int ao,int dor,int an,int dn){
 ifstream f(p);if(!f)return {};
 vector<int>ready(n+1,0);long long area=0;string line;int count=0;
 while(getline(f,line)){
  istringstream is(line);vector<string> tok;string a;while(is>>a)tok.push_back(a);
  if(tok.empty())continue;
  if(tok.size()>=3 && (tok[1]=="NOT"||tok[1]=="AND2"||tok[1]=="OR2")){
    int id=stoi(tok[0]);int u=stoi(tok[2]);int v=0;bool unary=tok[1]=="NOT";
    if(!unary){if(tok.size()!=4)return {};v=stoi(tok[3]);}else if(tok.size()!=3)return {};
    if(id!=n+1+count ||u<0||u>=id||v<0||v>=id)return {};
    if(unary){ready.push_back(ready[u]+dn);area+=an;}
    else if(tok[1]=="AND2"){ready.push_back(max(ready[u],ready[v])+da);area+=aa;}
    else{ready.push_back(max(ready[u],ready[v])+dor);area+=ao;}
    ++count;
  }else{
    if((int)tok.size()!=m)return {};
    int d=0;for(auto &t:tok){int v=stoi(t);if(v<0||v>=(int)ready.size())return {};d=max(d,ready[v]);}
    return {true,area,d};
  }
 }
 return {};
}
int main(int argc,char **argv){
 if(argc<3)return 2;
 const string input=argv[1],output=argv[2];
 ifstream in(input);int n,m,aa,da,ao,dor,an,dn,target;if(!(in>>n>>m))return 3;
 string line;getline(in,line);getline(in,line);
 if(!(in>>aa>>da>>ao>>dor>>an>>dn>>target))return 4;
 const char* child=getenv("SYNTH_CHILD");string binary=child?child:"./cubes_support";
 char t1[]="/tmp/ufugnet1_XXXXXX",t2[]="/tmp/ufugnet2_XXXXXX";
 int fd1=mkstemp(t1),fd2=mkstemp(t2);if(fd1<0||fd2<0)return 5;close(fd1);close(fd2);
 auto run=[&](const char*out,const char*ord)->Score{
   pid_t pid=fork();if(pid<0)return {};
   if(!pid){setenv("FAST","1",1);setenv("CUBEMODE","1",1);setenv("ORDER",ord,1);
      execl(binary.c_str(),binary.c_str(),input.c_str(),out,(char*)NULL);_exit(127);}
   int status;waitpid(pid,&status,0);if(!WIFEXITED(status)||WEXITSTATUS(status)!=0)return {};
   return evalFile(out,n,m,aa,da,ao,dor,an,dn);
 };
 auto a=run(t1,"natural");auto b=run(t2,"influence-desc");
 auto better=[&](Score x,Score y)->bool{
   if(!x.valid)return false;if(!y.valid)return true;
   bool xm=x.delay<=target,ym=y.delay<=target;
   if(xm!=ym)return xm;
   if(xm){if(x.area!=y.area)return x.area<y.area;return x.delay<y.delay;}
   if(x.delay!=y.delay)return x.delay<y.delay;return x.area<y.area;
 };
 const char *chosen=better(b,a)?t2:t1;
 ifstream src(chosen,ios::binary);ofstream dst(output,ios::binary);dst<<src.rdbuf();
 unlink(t1);unlink(t2);
 return dst&&src?0:6;
}
