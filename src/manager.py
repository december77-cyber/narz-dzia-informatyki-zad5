from src.models import Apartment, ApartmentSettlement, Bill, Parameters, Tenant, TenantSettlement, Transfer


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key, year=None, month=None):
        if apartment_key not in self.apartments:
            return None

        if month is not None and (month < 1 or month > 12):
            return None

        total = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key:
                if (year is None or bill.settlement_year == year) and (month is None or bill.settlement_month == month):
                    total += bill.amount_pln
        return total

    def create_apartment_settlement(self, apartment_key, year, month):
        costs = self.get_apartment_costs(apartment_key, year, month)
        if costs is None:
            return None

        return ApartmentSettlement(
            apartment=apartment_key,
            year=year,
            month=month,
            total_rent_pln=0.0,
            total_bills_pln=costs,
            total_due_pln=costs
        )

    def create_tenants_settlements(self, apartment_settlement):
        if apartment_settlement is None:
            return []

        tenants = []
        for key, tenant in self.tenants.items():
            if tenant.apartment == apartment_settlement.apartment:
                tenants.append(key)

        if not tenants:
            return []

        bills_share = apartment_settlement.total_bills_pln / len(tenants)

        result = []
        for key in tenants:
            settlement = TenantSettlement(
                tenant=key,
                apartment_settlement=apartment_settlement.apartment,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                rent_pln=0.0,
                bills_pln=bills_share,
                total_due_pln=bills_share,
                balance_pln=-bills_share
            )
            result.append(settlement)

        return result

