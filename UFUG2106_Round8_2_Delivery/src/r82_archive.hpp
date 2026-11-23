#pragma once
// R8.2: branch-level weighted objective and bounded Pareto collection.
// All comparisons use exact metrics for the COMPLETE live DAG.
#include <string>
#include <vector>
#include <algorithm>
#include <limits>
#include <cstdint>
namespace r82 {
struct Point {std::string mode;long long area=0;int delay=0;};
inline bool dominates(const Point&a,const Point&b){
 return a.area<=b.area&&a.delay<=b.delay&&(a.area<b.area||a.delay<b.delay);
}
inline std::vector<Point>pareto(const std::vector<Point>&p){
 std::vector<Point>out;
 for(size_t i=0;i<p.size();++i){bool lost=false;
   for(size_t j=0;j<p.size();++j)if(i!=j && (dominates(p[j],p[i]) ||
       (p[i].area==p[j].area&&p[i].delay==p[j].delay&&j<i))){lost=true;break;}
   if(!lost)out.push_back(p[i]);
 }
 return out;
}
inline int delay_cap(const Point &base,int target,const std::string&objective){
 if(objective=="strict")return base.delay;
 if(objective=="slack")return std::min(target,base.delay+std::max(0,(target-base.delay)/3));
 return target;
}
inline bool eligible(const Point&base,const Point&p,int target,const std::string&objective){
 if(p.area<=0||p.delay<0||p.delay>delay_cap(base,target,objective))return false;
 if(objective=="adp"){
  return p.area<=base.area &&
    (__int128)p.area*p.delay<(__int128)base.area*base.delay;
 }
 return (p.area<base.area)||(p.area==base.area&&p.delay<base.delay);
}
inline bool better(const Point&a,const Point&b,const std::string&objective){
 if(objective=="adp"){
  const __int128 x=(__int128)a.area*a.delay,y=(__int128)b.area*b.delay;
  if(x!=y)return x<y;
 }
 if(a.area!=b.area)return a.area<b.area;
 return a.delay<b.delay;
}
}
