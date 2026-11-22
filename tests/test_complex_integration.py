

from src.manager import Manager
from src.models import Parameters
from src.models import Bill


def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0

    # Nieprawidłowy miesiąc (np. 13 lub 0)
    assert manager.get_apartment_costs('apart-polanka', 2024, 13) is None
    assert manager.get_apartment_costs('apart-polanka', 2024, 0) is None


def test_create_apartment_settlement():
    manager = Manager(Parameters())

    # 1. Mieszkanie, które ma rachunki w danym miesiącu (styczeń 2025: 760.0 + 150.0 = 910.0)
    settlement_with_bills = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    assert settlement_with_bills is not None
    assert settlement_with_bills.apartment == 'apart-polanka'
    assert settlement_with_bills.year == 2025
    assert settlement_with_bills.month == 1
    assert settlement_with_bills.total_rent_pln == 0.0
    assert settlement_with_bills.total_bills_pln == 910.0
    assert settlement_with_bills.total_due_pln == 910.0

    # 2. Mieszkanie, które nie ma rachunków w danym miesiącu (luty 2025: 0.0)
    settlement_no_bills = manager.create_apartment_settlement('apart-polanka', 2025, 2)
    assert settlement_no_bills is not None
    assert settlement_no_bills.apartment == 'apart-polanka'
    assert settlement_no_bills.year == 2025
    assert settlement_no_bills.month == 2
    assert settlement_no_bills.total_rent_pln == 0.0
    assert settlement_no_bills.total_bills_pln == 0.0
    assert settlement_no_bills.total_due_pln == 0.0

    # 3. Nieistniejące mieszkanie
    assert manager.create_apartment_settlement('nie-istnieje', 2025, 1) is None


def test_create_tenants_settlements():
    manager = Manager(Parameters())
    apt_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)

    # 1. Mieszkanie ma 3 najemców (rachunki 910.0 dzielone na 3)
    res = manager.create_tenants_settlements(apt_settlement)
    assert len(res) == 3
    assert res[0].year == 2025
    assert res[0].month == 1
    assert res[0].bills_pln == 910.0 / 3
    assert res[1].bills_pln == 910.0 / 3
    assert res[2].bills_pln == 910.0 / 3

    # 2. Mieszkanie ma 1 najemcę (całe 910.0 dla niego)
    manager.tenants = {'tenant-1': manager.tenants['tenant-1']}
    res_one = manager.create_tenants_settlements(apt_settlement)
    assert len(res_one) == 1
    assert res_one[0].tenant == 'tenant-1'
    assert res_one[0].bills_pln == 910.0
    assert res_one[0].total_due_pln == 910.0
    assert res_one[0].balance_pln == -910.0

    # 3. Mieszkanie nie ma najemców
    manager.tenants = {}
    res_empty = manager.create_tenants_settlements(apt_settlement)
    assert res_empty == []


