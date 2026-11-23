// Standalone low-RSS process controller: fork+exec, wait4 on THIS child.
// Launching directly from Python and calling os.wait4 can erroneously
// include Python's high pre-exec RSS in the child's ru_maxrss peak.
#include <cstdio>
#include <cstdlib>
#include <cerrno>
#include <cstring>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <unistd.h>
int main(int argc,char **argv){
  if(argc<3){std::fprintf(stderr,"usage: peak_runner executable input output\n");return 2;}
  pid_t pid=fork();
  if(pid<0){std::perror("fork");return 3;}
  if(pid==0){execvp(argv[1],argv+1);std::perror("execvp");_exit(127);}
  int status=0;struct rusage ru{};
  if(wait4(pid,&status,0,&ru)<0){std::perror("wait4");return 4;}
  int code=WIFEXITED(status)?WEXITSTATUS(status):128+(WIFSIGNALED(status)?WTERMSIG(status):0);
  std::fprintf(stderr,"R821_PEAK_RSS_KIB=%ld R821_CHILD_EXIT=%d\n",ru.ru_maxrss,code);
  return code;
}
