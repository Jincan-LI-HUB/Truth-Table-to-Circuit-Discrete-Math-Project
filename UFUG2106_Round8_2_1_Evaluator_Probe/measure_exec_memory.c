#include <stdio.h>
#include <string.h>
#include <sys/resource.h>
int main(void) {
    struct rusage r;
    if (getrusage(RUSAGE_SELF, &r) != 0) return 2;
    printf("getrusage ru_maxrss=%ld KiB\n",r.ru_maxrss);
    FILE *f=fopen("/proc/self/status","r");
    if(!f)return 3;
    char line[256];
    while(fgets(line,sizeof line,f))
        if(!strncmp(line,"VmPeak:",7)||!strncmp(line,"VmRSS:",6)||!strncmp(line,"VmHWM:",6))
            fputs(line,stdout);
    fclose(f);
    return 0;
}
