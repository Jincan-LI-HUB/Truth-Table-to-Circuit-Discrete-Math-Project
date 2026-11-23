/* Low-overhead executable launcher. Avoids Python fork -> exec inherited
   pre-exec address space from corrupting the child ru_maxrss observation. */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <time.h>
#include <unistd.h>
#include <signal.h>

static long read_field(pid_t pid,const char *label){
    char path[100], line[256];snprintf(path,sizeof path,"/proc/%ld/status",(long)pid);
    FILE *f=fopen(path,"r");if(!f)return -1;
    long result=-1;
    while(fgets(line,sizeof line,f)){
       if(strncmp(line,label,strlen(label))==0){
           char *p=strchr(line,':');
           if(p)result=strtol(p+1,NULL,10);
           break;
       }
    }
    fclose(f);return result;
}
int main(int argc,char **argv){
   if(argc!=4){fprintf(stderr,"usage: %s PROGRAM INPUT OUTPUT\n",argv[0]);return 2;}
   pid_t pid=fork();if(pid<0){perror("fork");return 3;}
   if(pid==0){execl(argv[1],argv[1],argv[2],argv[3],(char *)NULL);perror("exec");_exit(127);}
   long peak_vm=0,peak_rss=0,peak_hwm=0;
   struct timespec delay={0,500000};
   int status=0;struct rusage usage;memset(&usage,0,sizeof usage);
   int done=0;
   while(!done){
       long z=read_field(pid,"VmPeak:");if(z>peak_vm)peak_vm=z;
       z=read_field(pid,"VmRSS:");if(z>peak_rss)peak_rss=z;
       z=read_field(pid,"VmHWM:");if(z>peak_hwm)peak_hwm=z;
       pid_t w=wait4(pid,&status,WNOHANG,&usage);
       if(w==pid)done=1;
       else if(w<0){perror("wait4");return 4;}
       else nanosleep(&delay,NULL);
   }
   int rc=WIFEXITED(status)?WEXITSTATUS(status):WIFSIGNALED(status)?128+WTERMSIG(status):255;
   printf("diagnostic_runner child_exit=%d ru_maxrss_kib=%ld sampled_vmpeak_kib=%ld sampled_vmhwm_kib=%ld sampled_rss_kib=%ld\n",
          rc,usage.ru_maxrss,peak_vm,peak_hwm,peak_rss);
   return rc;
}
