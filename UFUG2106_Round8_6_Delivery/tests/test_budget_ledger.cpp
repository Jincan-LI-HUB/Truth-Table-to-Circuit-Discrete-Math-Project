#include "../integration/budget_ledger.hpp"
#include <cassert>
#include <iostream>
int main(){
 using r85integration::BudgetLedger;
 BudgetLedger busy{1000,80,150,true};
 BudgetLedger skipped{1000,80,150,false};
 assert(busy.bdd_deadline_ms()==770);
 assert(skipped.bdd_deadline_ms()==920);
 assert(skipped.bdd_deadline_ms()-busy.bdd_deadline_ms()==150);
 assert(busy.bdd_remaining_ms(300)==470);
 assert(skipped.bdd_remaining_ms(300)==620);
 BudgetLedger unlimited{0,80,150,false};
 assert(unlimited.bdd_deadline_ms()==0);
 assert(unlimited.bdd_remaining_ms(500)==0);
 BudgetLedger too_tight{50,80,150,true};
 assert(too_tight.bdd_remaining_ms(100)==0);
 std::cout << "PASS integration budget contract simulation (NOT integrated code)\n";
}
