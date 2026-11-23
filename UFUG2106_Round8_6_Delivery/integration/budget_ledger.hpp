#pragma once
// A reference budget-accounting contract for Stage 2 integration.
// This is NOT wired to the teammate's integrated solver. It documents the
// mathematical invariant for refunding the reservation of a skipped optional
// mapper; no hidden-case behavior is claimed.
#include <algorithm>
#include <cstdint>
namespace r85integration {
struct BudgetLedger {
  std::int64_t time_limit_ms;
  std::int64_t output_reserve_ms;
  std::int64_t optional_mapper_reserve_ms;
  bool optional_mapper_admitted;
  std::int64_t bdd_deadline_ms() const {
    if(time_limit_ms<=0)return 0; // 0 = unrestricted by input contract
    const std::int64_t held = optional_mapper_admitted ?
        std::max<std::int64_t>(0,optional_mapper_reserve_ms):0;
    return std::max<std::int64_t>(0,time_limit_ms-
        std::max<std::int64_t>(0,output_reserve_ms)-held);
  }
  std::int64_t bdd_remaining_ms(std::int64_t elapsed_ms)const{
    if(time_limit_ms<=0)return 0;
    return std::max<std::int64_t>(0,bdd_deadline_ms()-
               std::max<std::int64_t>(0,elapsed_ms));
  }
};
}
