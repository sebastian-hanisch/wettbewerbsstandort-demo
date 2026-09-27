"""Szenario: Zufallsnetze und die Straße - ganzzahlig, deterministisch, in den erwarteten Grenzen."""

import pytest

import cmp_scenario as sc


def test_distance_is_integer_euclid_in_tenths():
    assert sc.distance((0, 0), (3, 4)) == 50 and sc.distance((5, 5), (5, 5)) == 0 and sc.distance((0, 0), (1, 1)) == 14


@pytest.mark.parametrize("kind", ["uniform", "cluster"])
def test_random_nets_are_deterministic_integer_and_symmetric(kind):
    a = sc.generate(14, kind, 1)
    assert a == sc.generate(14, kind, 1) and a != sc.generate(14, kind, 2)
    assert a.n == 14 and all(0 <= x < sc.MAP_W and 0 <= y < sc.MAP_W for x, y in a.pos) and all(sc.W_MIN <= w <= sc.W_MAX for w in a.w)
    assert all(isinstance(v, int) for row in a.d for v in row)
    assert all(a.d[i][i] == 0 for i in range(a.n)) and all(a.d[i][j] == a.d[j][i] for i in range(a.n) for j in range(a.n))


def test_clusters_are_more_concentrated_than_uniform_points():
    def mean_nn(net):
        return sum(min(net.d[i][j] for j in range(net.n) if j != i) for i in range(net.n)) / net.n
    assert sum(mean_nn(sc.generate(24, "cluster", s)) for s in range(10)) < sum(mean_nn(sc.generate(24, "uniform", s)) for s in range(10))


@pytest.mark.parametrize("n", [8, 9, 14, 15, 24])
def test_street_has_equal_neighbour_distances_and_equal_demand(n):
    net = sc.generate(n, "street", 5)
    gaps = {net.d[k][k + 1] for k in range(n - 1)}
    assert len(gaps) == 1 and set(net.w) == {sc.STREET_W} and len({p[0] for p in net.pos}) == n and all(p[1] == 50 for p in net.pos)
    assert net == sc.generate(n, "street", 99)                 # der Seed spielt keine Rolle


def test_unknown_kind_raises():
    with pytest.raises(KeyError):
        sc.generate(10, "kreis", 1)


def test_total_is_the_sum_of_the_demand():
    net = sc.generate(14, "uniform", 3)
    assert net.total == sum(net.w) and net.total > 0
