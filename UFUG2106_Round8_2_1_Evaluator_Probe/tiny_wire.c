/* Diagnostic-only wire circuit generator. NOT a submission synthesizer.
   Valid only for the probe's f(x)=x_(n-1), m=1 test fixtures. */
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <string.h>

static void record_memory(void) {
    const char *p=getenv("R821_MEMORY_PROBE_LOG");
    if (!p || !*p) return;
    FILE *out=fopen(p,"w"); if(!out) return;
    struct rusage u;
    if(getrusage(RUSAGE_SELF,&u)==0)
        fprintf(out,"ru_maxrss_kib=%ld\n",u.ru_maxrss);
    FILE *s=fopen("/proc/self/status","r");
    if(s){char line[256];
        while(fgets(line,sizeof line,s))
            if(!strncmp(line,"VmPeak:",7)||!strncmp(line,"VmHWM:",6)||
               !strncmp(line,"VmRSS:",6)||!strncmp(line,"VmSize:",7))
               fputs(line,out);
        fclose(s);
    }
    fclose(out);
}
int main(int argc,char **argv){
    if(argc!=3)return 2;
    FILE *in=fopen(argv[1],"r");if(!in)return 3;
    int n=0,m=0;
    if(fscanf(in,"%d%d",&n,&m)!=2 || n<1||n>20||m!=1){fclose(in);return 4;}
    fclose(in);
    FILE *out=fopen(argv[2],"w");if(!out)return 5;
    fprintf(out,"%d\n",n);
    int ok=!fclose(out);
    record_memory();
    return ok?0:6;
}
