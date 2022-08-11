import smartpy as sp

class LinkMe(sp.Contract):
    def __init__(self, val):
        self.init(
            owner = sp.test_account("owner").address,
            minimum_investment = sp.tez(val),
            investors = sp.map(l={}, tkey=sp.TAddress, tvalue = sp.TMutez),
            my_investments = sp.map(l={}, tkey=sp.TAddress, tvalue=sp.TMutez),
            employ_or_vendor = sp.map(l={}, tkey=sp.TAddress, tvalue = sp.TMutez),
            requests = sp.map(l = {}, tkey=sp.TAddress, tvalue=sp.TNat),
            cap_table = sp.map(l = {}, tkey = sp.TAddress, tvalue=sp.TNat),
            black_list = sp.map(l = {}, tkey = sp.TAddress, tvalue = sp.TNat),
            eval = sp.nat(0)
        )

    @sp.entry_point
    def invest(self):

        sp.verify(sp.amount >= self.data.minimum_investment, "INVALID AMOUNT")
        
        sp.if ~self.data.investors.contains(sp.sender):
            self.data.investors[sp.sender] = sp.amount
            self.data.my_investments[self.data.owner] = sp.amount 
        sp.else:
            self.data.investors[sp.sender] += sp.amount
            self.data.my_investments[self.data.owner] += sp.amount 

    @sp.entry_point
    def pay_employ_or_vendor(self, id):
        sp.set_type(id, sp.TAddress)
        # Sanity checks
        sp.verify(sp.sender == self.data.owner, "UNAUTHORISED ACCESS")
        sp.verify(self.data.employ_or_vendor.contains(id), "INVALID ACCOUNT")
        sp.verify(self.data.employ_or_vendor[id] != sp.tez(0), "PAYMENTS MADE")
        # Pay employs/vendors
        sp.send(id, self.data.employ_or_vendor[id])
        self.data.employ_or_vendor[id] = sp.tez(0)
    
    @sp.entry_point
    def join(self):
        sp.verify(self.data.black_list.contains(sp.sender) == False, "YOU ARE BLACKLISTED")
        sp.verify(self.data.requests.contains(sp.sender) == False, "REQUEST ALREADY SENT")
        #sp.verify(~self.data.employ_or_vendor.contains(sp.sender), "ALREADY JOINED")
        self.data.requests[sp.sender] = 0

    #@sp.entry_point
    #def accept(self, id, salary):
    #    sp.set_type(id, sp.TAddress)
    #    sp.set_type(salary, sp.TMutez)
    #    sp.verify(sp.sender == self.data.owner, "UNAUTHORISED ACCESS")
    #    sp.verify(self.data.requests.contains(id), "INVALID ADDRESS")
    #    self.data.employ_or_vendor[id] = salary
    #    del self.data.requests[id]

    @sp.entry_point
    def reject(self, id):
        sp.set_type(id, sp.TAddress)
        sp.verify(sp.sender == self.data.owner, "UNAUTHORISED ACCESS")
        sp.verify(self.data.requests.contains(id), "INVALID ADDRESS")
        self.data.black_list[id] = 0
        del self.data.requests[id]

    @sp.entry_point
    def remove_from_job(self, id):
        sp.set_type(id, sp.TAddress)

        sp.verify(sp.sender == self.data.owner, "UNAUTHORISED ACCESS")
        sp.verify(self.data.employ_or_vendor.contains(id), "INVALID ADDRESS")

        del self.data.employ_or_vendor[id]
        self.data.black_list[id] = 0

    @sp.entry_point
    def remove_from_blacklist(self, id):
        sp.set_type(id, sp.TAddress)

        sp.verify(sp.sender == self.data.owner, "UNAUTHORISED ACCESS")
        sp.verify(self.data.black_list.contains(id), "INVALID ADDRESS")
        del self.data.black_list[id]

    @sp.entry_point
    def update_record(self, id, salary):
        sp.set_type(id, sp.TAddress)
        sp.set_type(salary, sp.TMutez)

        sp.verify(sp.sender == self.data.owner, "UNAUTHORISED ACCESS")
        sp.verify(self.data.employ_or_vendor.contains(id), "INVALID ADDRESS")

        self.data.employ_or_vendor[id] = salary

    @sp.entry_point
    #def update_cap_table(self, amount):
    #    sp.set_type(amount, sp.TNat)

    #    sp.verify(sp.sender == self.data.owner, "UNAUTHORISED ACCESS")
    #    sp.verify(amount > sp.as_nat(self.data.minimum_investment)*sp.len(self.data.investors), "INVALID AMOUNT")

        #sp.for self.data.eval in range(self.data.investors.keys()):
        #    sp.if self.data.cap_table.contains(id) == False:
        #        self.data.cap_table[id] = sp.as_nat(self.data.investors[id])/eval * 100
            

    #@sp.entry_point
    #def send_SAFE_or_SAFT(self, id):
    #    sp.set_type(id, sp.TAddress)

    #    sp.verify(sp.sender == self.data.owner, "UNAUTHORISED ACCESS")
    #    sp.verify(self.data.investors.contains(id), "INVALID ADDRESS")

    @sp.add_test(name="main")
    def test():
        scenario = sp.test_scenario()

        # Test address
        owner = sp.test_account("owner")
        alice = sp.test_account("alice")

        # Create contract
        contract = LinkMe(2)
        scenario += contract

        # invest
        scenario.h2("Invested")
        scenario += contract.invest().run(sender = alice, amount = sp.tez(7))   

        # investment failed
        scenario.h2("Investment Failed")
        scenario += contract.invest().run(sender = alice, amount = sp.tez(1), valid = False)
