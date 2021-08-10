import itertools

import numpy as np
import pandas as pd
import pytest

import staircase.test_data as test_data
from staircase import Stairs


def _expand_interval_definition(start, end=None, value=1):
    return start, end, value


def _compare_iterables(it1, it2):
    it1 = [i for i in it1 if i is not None]
    it2 = [i for i in it2 if i is not None]
    if len(it2) != len(it1):
        return False
    for e1, e2 in zip(it1, it2):
        if e1 != e2:
            return False
    return True


def s1(closed="left"):
    int_seq1 = Stairs(initial_value=0, closed=closed)
    int_seq1.layer(1, 10, 2)
    int_seq1.layer(-4, 5, -1.75)
    int_seq1.layer(3, 5, 2.5)
    int_seq1.layer(6, 7, -2.5)
    int_seq1.layer(7, 10, -2.5)
    return int_seq1


def s2():
    int_seq2 = Stairs(initial_value=0)
    int_seq2.layer(1, 7, -2.5)
    int_seq2.layer(8, 10, 5)
    int_seq2.layer(2, 5, 4.5)
    int_seq2.layer(2.5, 4, -2.5)
    int_seq2.layer(-2, 1, -1.75)
    return int_seq2


def s3():  # boolean
    int_seq = Stairs(initial_value=0)
    int_seq.layer(-10, 10, 1)
    int_seq.layer(-8, -7, -1)
    int_seq.layer(-5, -2, -1)
    int_seq.layer(0.5, 1, -1)
    int_seq.layer(3, 3.5, -1)
    int_seq.layer(7, 9.5, -1)
    return int_seq


def s4():  # boolean
    int_seq = Stairs(initial_value=0)
    int_seq.layer(-11, 9, 1)
    int_seq.layer(-9.5, -8, -1)
    int_seq.layer(-7.5, -7, -1)
    int_seq.layer(0, 3, -1)
    int_seq.layer(6, 6.5, -1)
    int_seq.layer(7, 8.5, -1)
    return int_seq


@pytest.fixture
def s1_fix():
    return s1()


@pytest.fixture
def s2_fix():
    return s2()


@pytest.fixture
def s3_fix():
    return s3()


@pytest.fixture
def s4_fix():
    return s4()


def test_init():
    assert Stairs(initial_value=0).identical(Stairs())
    assert Stairs().identical(Stairs(initial_value=0))


@pytest.mark.parametrize("init_value", [0, 1.25, -1.25, 2, -2])
def test_init2(init_value):
    int_seq = Stairs(initial_value=init_value)
    assert (
        int_seq.number_of_steps == 0
    ), "Initialised Stairs should have exactly one interval"


@pytest.mark.parametrize("init_value", [0, 1.25, -1.25, 2, -2])
def test_init3(init_value):
    int_seq = Stairs(initial_value=init_value)
    assert (
        len(int_seq.step_points) == 0
    ), "Initialised Stairs should not have any finite interval endpoints"


@pytest.mark.parametrize("init_value", [0, 1.25, -1.25, 2, -2])
def test_init4(init_value):
    int_seq = Stairs(initial_value=init_value)
    assert (
        int_seq(-1) == init_value
    ), "Initialised Stairs should have initial value everywhere"
    assert (
        int_seq(0) == init_value
    ), "Initialised Stairs should have initial value everywhere"
    assert (
        int_seq(1) == init_value
    ), "Initialised Stairs should have initial value everywhere"


@pytest.mark.parametrize(
    "init_value, added_interval",
    itertools.product(
        [0, 1.25, -1.25],
        [(-2, 1), (3, 5, 2), (1, 5, -1), (-5, -3, 3), (3,), (2, None, 2)],
    ),
)
def test_one_finite_interval(init_value, added_interval):
    e = 0.0001
    int_seq = Stairs(initial_value=init_value)
    int_seq.layer(*added_interval)
    start, end, value = _expand_interval_definition(*added_interval)
    assert int_seq.number_of_steps == 2 - (
        end is None
    ), "One finite interval added to initial infinite interval should result in 3 intervals"
    assert _compare_iterables(
        int_seq.step_points, (start, end)
    ), "Finite endpoints are not what is expected"
    assert (
        int_seq(float("-inf")) == init_value
    ), "Adding finite interval should not change initial value"
    assert int_seq(float("inf")) == init_value + value * (
        end is None
    ), "Adding finite interval should not change final value"
    assert int_seq(start - e) == init_value
    assert int_seq(start) == init_value + value
    assert int_seq(start + e) == init_value + value
    if end is not None:
        assert int_seq(end - e) == init_value + value
        assert int_seq(end) == init_value


@pytest.mark.parametrize(
    "init_value, endpoints, value",
    itertools.product(
        [0, 1.25, -1.25, 2, -2],
        [(-2, 1, 3), (-2, -1, 3), (-3, -2, -1), (1, 2, 3)],
        [-1, 2, 3],
    ),
)
def test_two_adjacent_finite_interval_same_value(init_value, endpoints, value):
    e = 0.0001
    int_seq = Stairs(initial_value=init_value)
    point1, point2, point3 = endpoints
    int_seq.layer(point1, point2, value)
    int_seq.layer(point2, point3, value)
    assert int_seq.number_of_steps == 2, "Expected result to be 3 intervals"
    assert _compare_iterables(
        int_seq.step_points, (point1, point3)
    ), "Finite endpoints are not what is expected"
    assert (
        int_seq(float("-inf")) == init_value
    ), "Adding finite interval should not change initial value"
    assert (
        int_seq(float("inf")) == init_value
    ), "Adding finite interval should not change final value"
    assert int_seq(point1 - e) == init_value
    assert int_seq(point1) == init_value + value
    assert int_seq(point2) == init_value + value
    assert int_seq(point3 - e) == init_value + value
    assert int_seq(point3) == init_value


@pytest.mark.parametrize(
    "init_value, endpoints, value, delta",
    itertools.product(
        [0, 1.25, -1.25, 2, -2],
        [(-2, 1, 3), (-2, -1, 3), (-3, -2, -1), (1, 2, 3)],
        [-1, 2, 4],
        [3, -3, 1.5, -1.5],
    ),
)
def test_two_adjacent_finite_interval_different_value(
    init_value, endpoints, value, delta
):
    e = 0.0001
    int_seq = Stairs(initial_value=init_value)
    point1, point2, point3 = endpoints
    int_seq.layer(point1, point2, value)
    int_seq.layer(point2, point3, value + delta)
    assert int_seq.number_of_steps == 3, "Expected result to be 4 intervals"
    assert _compare_iterables(
        int_seq.step_points, (point1, point2, point3)
    ), "Finite endpoints are not what is expected"
    assert (
        int_seq(float("-inf")) == init_value
    ), "Adding finite interval should not change initial value"
    assert (
        int_seq(float("inf")) == init_value
    ), "Adding finite interval should not change final value"
    assert int_seq(point1 - e) == init_value
    assert int_seq(point1) == init_value + value
    assert int_seq(point2) == init_value + value + delta
    assert int_seq(point3 - e) == init_value + value + delta
    assert int_seq(point3) == init_value


@pytest.mark.parametrize(
    "init_value, endpoints, value, delta",
    itertools.product(
        [0, 1.25, -1.25, 2, -2],
        [(-2, 1, 2, 3), (-3, -2, -1, 3), (-4, -3, -2, -1), (0, 1, 2, 3)],
        [-1, 2, 4],
        [3, -3, 1.5, -1.5],
    ),
)
def test_two_overlapping_finite_interval(init_value, endpoints, value, delta):
    e = 0.0001
    int_seq = Stairs(initial_value=init_value)
    point1, point2, point3, point4 = endpoints
    int_seq.layer(point1, point3, value)
    int_seq.layer(point2, point4, value + delta)
    assert int_seq.number_of_steps == 4, "Expected result to be 5 intervals"
    assert _compare_iterables(
        int_seq.step_points, (point1, point2, point3, point4)
    ), "Finite endpoints are not what is expected"
    assert (
        int_seq(float("-inf")) == init_value
    ), "Adding finite interval should not change initial value"
    assert (
        int_seq(float("inf")) == init_value
    ), "Adding finite interval should not change final value"
    assert int_seq(point1 - e) == init_value
    assert int_seq(point1) == init_value + value
    assert int_seq(point2) == init_value + 2 * value + delta
    assert int_seq(point3 - e) == init_value + 2 * value + delta
    assert int_seq(point3) == init_value + value + delta
    assert int_seq(point4 - e) == init_value + value + delta
    assert int_seq(point4) == init_value


@pytest.mark.parametrize(
    "init_value, endpoints, value, delta",
    itertools.product(
        [0, 1.25, -1.25, 2, -2],
        [(-2, 1, 2, 3), (-3, -2, -1, 3), (-4, -3, -2, -1), (0, 1, 2, 3)],
        [-1, 2, 4],
        [3, -3, 1.5, -1.5],
    ),
)
def test_two_finite_interval_one_subinterval(init_value, endpoints, value, delta):
    e = 0.0001
    int_seq = Stairs(initial_value=init_value)
    point1, point2, point3, point4 = endpoints
    int_seq.layer(point1, point4, value)
    int_seq.layer(point2, point3, value + delta)
    assert int_seq.number_of_steps == 4, "Expected result to be 5 intervals"
    assert _compare_iterables(
        int_seq.step_points, (point1, point2, point3, point4)
    ), "Finite endpoints are not what is expected"
    assert (
        int_seq.initial_value == init_value
    ), "Adding finite interval should not change initial value"
    assert (
        int_seq(float("inf")) == init_value
    ), "Adding finite interval should not change final value"
    assert int_seq(point1 - e) == init_value
    assert int_seq(point1) == init_value + value
    assert int_seq(point2) == init_value + 2 * value + delta
    assert int_seq(point3 - e) == init_value + 2 * value + delta
    assert int_seq(point3) == init_value + value
    assert int_seq(point4 - e) == init_value + value
    assert int_seq(point4) == init_value


@pytest.mark.parametrize("init_value", [0, 1.25, -1.25, 2, -2])
def test_copy_and_equality(init_value):
    int_seq = Stairs(initial_value=init_value)
    int_seq_copy = int_seq.copy()
    assert int_seq.identical(int_seq_copy)
    assert int_seq_copy.identical(int_seq)


@pytest.mark.parametrize("init_value", [0, 1.25, -1.25, 2, -2])
def test_deepcopy(init_value):
    int_seq = Stairs(initial_value=init_value)
    int_seq_copy = int_seq.copy()
    int_seq_copy.layer(1, 2)
    assert not int_seq.identical(int_seq_copy)
    assert not int_seq_copy.identical(int_seq)


@pytest.mark.parametrize("init_value", [0, 1.25, -1.25, 2, -2])
def test_layer1(init_value):
    intervals_to_add = [(-2, 1), (3, 5), (1, 5), (-5, -3), (None, 0), (0, None)]
    int_seq = Stairs(initial_value=init_value)
    int_seq2 = Stairs(initial_value=init_value)
    for start, end in intervals_to_add:
        int_seq.layer(start, end)
    starts, ends = list(zip(*intervals_to_add))
    starts = [{None: np.nan}.get(x, x) for x in starts]
    ends = [{None: np.nan}.get(x, x) for x in ends]
    int_seq2.layer(starts, ends)
    assert int_seq.identical(int_seq2)
    assert int_seq2.identical(int_seq)


@pytest.mark.parametrize("init_value", [0, 1.25, -1.25, 2, -2])
def test_layer2(init_value):
    intervals_to_add = [(-2, 1, 1), (3, 5, 2), (1, 5, -1), (-5, -3, 3)]
    int_seq = Stairs(initial_value=init_value)
    int_seq2 = Stairs(initial_value=init_value)
    for interval in intervals_to_add:
        int_seq.layer(*interval)
    starts, ends, values = list(zip(*intervals_to_add))
    int_seq2.layer(starts, ends, values)
    assert int_seq.identical(int_seq2)
    assert int_seq2.identical(int_seq)


def test_make_boolean(s2_fix):
    int_seq = s2_fix
    calc = int_seq.make_boolean()
    expected = Stairs()
    expected.layer(-2, 7, 1)
    expected.layer(8, 10, 1)
    assert calc.identical(expected), "Boolean calculation not what it should be"
    assert expected.identical(calc), "Boolean calculation not what it should be"


def test_invert(s2_fix):
    int_seq = s2_fix
    calc = ~int_seq
    expected = Stairs(initial_value=1)
    expected.layer(-2, 7, -1)
    expected.layer(8, 10, -1)
    assert calc.identical(expected), "Invert calculation not what it should be"
    assert expected.identical(calc), "Invert calculation not what it should be"


def test_and(s3_fix, s4_fix):
    calc = s3_fix & s4_fix
    expected = Stairs(initial_value=0)
    expected.layer(-10, -9.5)
    expected.layer(-7, -5)
    expected.layer(-2, 0)
    expected.layer(3.5, 6)
    expected.layer(6.5, 7)
    assert calc.identical(expected), "AND calculation not what it should be"
    assert expected.identical(calc), "AND calculation not what it should be"


def test_or(s3_fix, s4_fix):
    calc = s3_fix | s4_fix
    expected = Stairs(initial_value=0)
    expected.layer(-11, -7.5)
    expected.layer(-7, 0.5)
    expected.layer(1, 7)
    expected.layer(8.5, 9)
    expected.layer(9.5, 10)
    assert calc.identical(expected), "OR calculation not what it should be"
    assert expected.identical(calc), "OR calculation not what it should be"


def test_lt(s1_fix, s2_fix):
    calc = s1_fix < s2_fix
    expected = Stairs(initial_value=0)
    expected.layer(-4, -2)
    expected.layer(2, 2.5)
    expected.layer(7, 10)
    assert calc.identical(expected), "LT calculation not what it should be"
    assert expected.identical(calc), "LT calculation not what it should be"


def test_gt(s1_fix, s2_fix):
    calc = s1_fix > s2_fix
    expected = Stairs(initial_value=0)
    expected.layer(1, 2)
    expected.layer(2.5, 7)
    assert calc.identical(expected), "GT calculation not what it should be"
    assert expected.identical(calc), "GT calculation not what it should be"


def test_le(s1_fix, s2_fix):
    calc = s1_fix <= s2_fix
    expected = Stairs(initial_value=1)
    expected.layer(1, 2, -1)
    expected.layer(2.5, 7, -1)
    assert calc.identical(expected), "LE calculation not what it should be"
    assert expected.identical(calc), "LE calculation not what it should be"


def test_ge(s1_fix, s2_fix):
    calc = s1_fix >= s2_fix
    expected = Stairs(initial_value=1)
    expected.layer(-4, -2, -1)
    expected.layer(2, 2.5, -1)
    expected.layer(7, 10, -1)
    assert calc.identical(expected), "GE calculation not what it should be"
    assert expected.identical(calc), "GE calculation not what it should be"


def test_eq_1(s1_fix, s2_fix):
    calc = s1_fix == s2_fix
    expected = Stairs(initial_value=1)
    expected.layer(-4, -2, -1)
    expected.layer(1, 10, -1)
    assert calc.identical(expected), "EQ calculation not what it should be"
    assert expected.identical(calc), "EQ calculation not what it should be"


def test_eq_2(s1_fix, s2_fix):
    calc = s1_fix == s2_fix
    expected = Stairs(initial_value=1)
    expected.layer(-4, -2, -1)
    expected.layer(1, 10, -1)
    assert calc.identical(expected), "EQ calculation not what it should be"
    assert expected.identical(calc), "EQ calculation not what it should be"


def test_ne(s1_fix, s2_fix):
    calc = s1_fix != s2_fix
    expected = Stairs(initial_value=0)
    expected.layer(-4, -2, 1)
    expected.layer(1, 10, 1)
    assert calc.identical(expected), "NOT EQUAL calculation not what it should be"
    assert expected.identical(calc), "NOT EQUAL calculation not what it should be"


@pytest.mark.parametrize("init_value", [0, 1.25, -1.25, 2, -2])
def test_base_integral_0_2(init_value):
    int_seq = Stairs(initial_value=init_value)
    assert int_seq.agg("integral", (0, 2)) == 2 * init_value


@pytest.mark.parametrize("init_value", [0, 1.25, -1.25, 2, -2])
def test_base_integral_neg1_1(init_value):
    int_seq = Stairs(initial_value=init_value)
    assert int_seq.agg("integral", (-1, 1)) == 2 * init_value


@pytest.mark.parametrize("init_value", [0, 1.25, -1.25, 2, -2])
def test_base_integral_neg2_0(init_value):
    int_seq = Stairs(initial_value=init_value)
    assert int_seq.agg("integral", (-2, 0)) == 2 * init_value


@pytest.mark.parametrize("init_value", [0, 1.25, -1.25, 2, -2])
def test_base_integral_point5_1(init_value):
    int_seq = Stairs(initial_value=init_value)
    assert int_seq.agg("integral", (0.5, 1)) == 0.5 * init_value


def test_integral1(s1_fix, s2_fix):
    assert s1_fix.integral() == -2.75
    assert s2_fix.integral() == -0.5


def test_integral2(s1_fix, s2_fix):
    assert s1_fix.agg("integral", (-1, 5.5)) == 3.5
    assert s2_fix.agg("integral", (-1, 5.5)) == -5


def test_mean1(s1_fix, s2_fix):
    assert abs(s1_fix.mean() - -0.19642857) < 0.000001
    assert abs(s2_fix.mean() - -0.04166666) < 0.000001


def test_mean2(s1_fix, s2_fix):
    assert abs(s1_fix.agg("mean", (2, 8)) - 1.125) < 0.000001
    assert abs(s2_fix.agg("mean", (2, 8)) - -0.45833333) < 0.000001


def test_integral_0():
    assert Stairs(initial_value=0).layer(None, 0).integral() == 0


def test_mean_nan():
    assert Stairs(initial_value=0).layer(None, 0).mean() is np.nan


def test_to_dataframe(s1_fix):
    s1_fix.to_frame()


@pytest.mark.parametrize(
    "stairs_instance, bounds, cuts",
    itertools.product(
        [s1(), s2(), s3(), s4()],
        [(3, 4), (0, 10), (-10, 30), (-5, -1)],
        ["unit", (0, 2.5, 4, 4.5, 7)],
    ),
)
def test_hist_left_closed(stairs_instance, bounds, cuts):
    def make_expected_result(interval_index, lower, upper):
        return pd.Series(
            [
                ((stairs_instance >= i.left) * (stairs_instance < i.right)).agg(
                    "mean", (lower, upper)
                )
                for i in interval_index
            ],
            index=interval_index,
            dtype="float64",
        )

    hist = stairs_instance.clip(*bounds).hist(bins=cuts, stat="probability")
    expected = make_expected_result(hist.index, *bounds)
    assert (hist.apply(round, 5) == expected.apply(round, 5)).all(), f"{bounds}, {cuts}"


@pytest.mark.parametrize(
    "stairs_instance, bounds, cuts",
    itertools.product(
        [s1(), s2(), s3(), s4()],
        [(3, 4), (0, 10), (-10, 30), (-5, -1)],
        ["unit", (0, 2.5, 4, 4.5, 7)],
    ),
)
def test_hist_right_closed(stairs_instance, bounds, cuts):
    def make_expected_result(interval_index, lower, upper):
        return pd.Series(
            [
                ((stairs_instance > i.left) * (stairs_instance <= i.right)).agg(
                    "mean", (lower, upper)
                )
                for i in interval_index
            ],
            index=interval_index,
            dtype="float64",
        )

    hist = stairs_instance.clip(*bounds).hist(
        bins=cuts, closed="right", stat="probability"
    )
    expected = make_expected_result(hist.index, *bounds)
    assert (hist.apply(round, 5) == expected.apply(round, 5)).all(), f"{bounds}, {cuts}"


@pytest.mark.parametrize(
    "stairs_instance, bounds, closed",
    itertools.product(
        [s1(), s2(), s3(), s4()],
        [(3, 4), (0, 10), (-10, 30), (-5, -1)],
        ["left", "right"],
    ),
)
def test_hist_default_bins(stairs_instance, bounds, closed):
    # really testing the default binning process here
    hist = stairs_instance.clip(*bounds).hist(closed=closed, stat="probability")
    assert abs(hist.sum() - 1) < 0.000001


# np.var(st1(np.linspace(-4,10, 10000000))) = 2.501594244387741
# np.var(st1(np.linspace(-5,10, 10000000))) = 2.3372686165530117
# np.var(st1(np.linspace(1,12, 10000000))) = 1.5433884747933315


@pytest.mark.parametrize(
    "bounds, expected",
    [
        ((), 2.501594244387741),
        (((-5, 10),), 2.3372686165530117),
        (((1, 12),), 1.5433884747933315),
    ],
)
def test_s1_var(bounds, expected):
    assert np.isclose(s1().agg("var", *bounds), expected, atol=0.0001)


# np.var(st2(np.linspace(-2, 10, 10000000))) = 7.024303861110942
# np.var(st2(np.linspace(-3, 7.5, 10000000))) = 2.2678568437499633
# np.var(st2(np.linspace(0, 14, 10000000))) = 5.538902194132663


@pytest.mark.parametrize(
    "bounds, expected",
    [
        ((), 7.024303861110942),
        (((-3, 7.5),), 2.2678568437499633),
        (((0, 14),), 5.538902194132663),
    ],
)
def test_s2_var(bounds, expected):
    assert np.isclose(s2().agg("var", *bounds), expected, atol=0.0001)


# np.std(st1(np.linspace(-4,10, 10000000))) = 1.5816428940780978
# np.std(st1(np.linspace(-5,10, 10000000))) = 1.528797568034358
# np.std(st1(np.linspace(1,12, 10000000))) = 1.242331869829206


@pytest.mark.parametrize(
    "bounds, expected",
    [
        ((), 1.5816428940780978),
        (((-5, 10),), 1.528797568034358),
        (((1, 12),), 1.242331869829206),
    ],
)
def test_s1_std(bounds, expected):
    assert np.isclose(s1().agg("std", *bounds), expected, atol=0.0001)


# np.std(st2(np.linspace(-2, 10, 10000000))) = 2.650340329299417
# np.std(st2(np.linspace(-3, 7.5, 10000000))) = 1.5059405179986238
# np.std(st2(np.linspace(0, 14, 10000000))) = 2.3534872411238315


@pytest.mark.parametrize(
    "bounds, expected",
    [
        ((), 2.650340329299417),
        (((-3, 7.5),), 1.5059405179986238),
        (((0, 14),), 2.3534872411238315),
    ],
)
def test_s2_std(bounds, expected):
    assert np.isclose(s2().agg("std", *bounds), expected, atol=0.0001)


# # np.cov(st1(pts[:-100000]), st1(pts[100000:]))[0,1] = 1.9386094481108465
# # np.cov(st1(np.linspace(-4, 8, 12*100000 + 1)), st1(np.linspace(-2, 10, 12*100000 + 1)))[0,1] = 1.1184896017794723
# # np.cov(st1(np.linspace(-4, 8, 12*100000 + 1)), st1.shift(-2)(np.linspace(-4, 8, 12*100000 + 1)))[0,1] = 1.1184896017794723


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"where": (-4, 10), "lag": 1}, 1.9386094481108465),
        ({"where": (-4, 10), "lag": 2}, 1.1184896017794723),
        ({"where": (-4, 8), "lag": 2, "clip": "post"}, 1.1184896017794723),
    ],
)
def test_s1_autocov(kwargs, expected):
    assert np.isclose(s1().cov(s1(), **kwargs), expected, atol=0.00001)


# # np.cov(st2(np.linspace(-2, 9, 11*100000 + 1)), st2(np.linspace(-1, 10, 11*100000 + 1)))[0,1 = 3.1022721590913256
# # np.cov(st2(np.linspace(0, 6, 12*100000 + 1)), st2(np.linspace(2, 8, 12*100000 + 1)))[0,1] = -0.7291746267294938
# # np.cov(st2(np.linspace(0, 6, 12*100000 + 1)), st2.shift(-2)(np.linspace(0, 6, 12*100000 + 1)))[0,1] = -0.7291746267294938


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"where": (-2, 10), "lag": 1}, 3.1022721590913256),
        ({"where": (0, 8), "lag": 2}, -0.7291746267294938),
        ({"where": (0, 6), "lag": 2, "clip": "post"}, -0.7291746267294938),
    ],
)
def test_s2_autocov(kwargs, expected):
    assert np.isclose(s2().cov(s2(), **kwargs), expected, atol=0.00001)


# # np.cov(st1(np.linspace(-2, 9, 11*100000 + 1)), st2(np.linspace(-1, 10, 11*100000 + 1)))[0,1 = -0.08677679611199672
# # np.cov(st1(np.linspace(0, 6, 12*100000 + 1)), st2(np.linspace(2, 8, 12*100000 + 1)))[0,1] = -1.970493123547197
# # np.cov(st1(np.linspace(0, 6, 12*100000 + 1)), st2.shift(-2)(np.linspace(0, 6, 12*100000 + 1)))[0,1] = -1.970493123547197


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"where": (-2, 10), "lag": 1}, -0.08677679611199672),
        ({"where": (0, 8), "lag": 2}, -1.970493123547197),
        ({"where": (0, 6), "lag": 2, "clip": "post"}, -1.970493123547197),
    ],
)
def test_crosscov(kwargs, expected):
    assert np.isclose(s1().cov(s2(), **kwargs), expected, atol=0.00001)


# # np.corrcoef(st1(pts[:-100000]), st1(pts[100000:]))[0,1] = 0.6927353407369307
# # np.corrcoef(st1(np.linspace(-4, 8, 12*100000 + 1)), st1(np.linspace(-2, 10, 12*100000 + 1)))[0,1] = -0.2147502741669856
# # np.corrcoef(st1(np.linspace(-4, 8, 12*100000 + 1)), st1.shift(-2)(np.linspace(-4, 8, 12*100000 + 1)))[0,1] = -0.2147502741669856


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"where": (-2, 10), "lag": 1}, 0.6927353407369307),
        ({"where": (0, 8), "lag": 2}, -0.2147502741669856),
        ({"where": (0, 6), "lag": 2, "clip": "post"}, -0.2147502741669856),
    ],
)
def test_s1_autocorr(kwargs, expected):
    assert np.isclose(s1().corr(s1(), **kwargs), expected, atol=0.00001)


# # np.corrcoef(st2(pts[:-100000]), st2(pts[100000:]))[0,1] = 0.5038199912440895
# # np.corrcoef(st2(np.linspace(-4, 8, 12*100000 + 1)), st2(np.linspace(-2, 10, 12*100000 + 1)))[0,1] = -0.2419504099129966
# # np.corrcoef(st2(np.linspace(-4, 8, 12*100000 + 1)), st2.shift(-2)(np.linspace(-4, 8, 12*100000 + 1)))[0,1] = -0.2419504099129966


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"where": (-2, 10), "lag": 1}, 0.5038199912440895),
        ({"where": (0, 8), "lag": 2}, -0.2419504099129966),
        ({"where": (0, 6), "lag": 2, "clip": "post"}, -0.2419504099129966),
    ],
)
def test_s2_autocorr(kwargs, expected):
    assert np.isclose(s2().corr(s2(), **kwargs), expected, atol=0.00001)


# # np.corrcoef(st1(pts[:-100000]), st2(pts[100000:]))[0,1] = -0.01966642657198049
# # np.corrcoef(st1(np.linspace(-4, 8, 12*100000 + 1)), st2(np.linspace(-2, 10, 12*100000 + 1)))[0,1] = -0.7086484036832666
# # np.corrcoef(st1(np.linspace(-4, 8, 12*100000 + 1)), st2.shift(-2)(np.linspace(-4, 8, 12*100000 + 1)))[0,1] = -0.7086484036832666


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"where": (-2, 10), "lag": 1}, -0.01966642657198049),
        ({"where": (0, 8), "lag": 2}, -0.7086484036832666),
        ({"where": (0, 6), "lag": 2, "clip": "post"}, -0.7086484036832666),
    ],
)
def test_crosscorr(kwargs, expected):
    assert np.isclose(s1().corr(s2(), **kwargs), expected, atol=0.00001)


@pytest.mark.parametrize(
    "kwargs, expected_index, expected_vals",
    [
        (
            {"window": (-1, 1)},
            [-5, -3, 0, 2, 4, 5, 6, 7, 9, 11],
            [0.0, -1.75, -1.75, 0.25, 2.75, 2.375, 0.75, -0.5, -0.5, 0.0],
        ),
        (
            {"window": (-2, 0)},
            [-4, -2, 1, 3, 5, 6, 7, 8, 10, 12],
            [0.0, -1.75, -1.75, 0.25, 2.75, 2.375, 0.75, -0.5, -0.5, 0.0],
        ),
        (
            {"window": (-1, 1), "where": (0, 8)},
            [1, 2, 4, 5, 6, 7],
            [-0.75, 0.25, 2.75, 2.375, 0.75, -0.5],
        ),
    ],
)
def test_s1_rolling_mean(s1_fix, kwargs, expected_index, expected_vals):
    rm = s1_fix.rolling_mean(**kwargs)
    assert list(rm.values) == expected_vals
    assert list(rm.index) == expected_index


@pytest.mark.parametrize(
    "closed, kwargs, expected_val",
    [
        (
            "left",
            {},
            -1.75,
        ),
        (
            "left",
            {"where": (1, 6)},
            0.25,
        ),
        (
            "right",
            {"where": (1, 6), "closed": "left"},
            -1.75,
        ),
        (
            "left",
            {"where": (1, 6), "closed": "right"},
            -0.5,
        ),
    ],
)
def test_s1_min(closed, kwargs, expected_val):
    from staircase.core import stats

    assert stats.min(s1(closed=closed), **kwargs) == expected_val


@pytest.mark.parametrize(
    "closed, kwargs, expected_val",
    [
        (
            "left",
            {},
            2.75,
        ),
        (
            "left",
            {"where": (-4, 1)},
            -1.75,
        ),
        (
            "right",
            {"where": (-4, 1), "closed": "left"},
            0.0,
        ),
        (
            "left",
            {"where": (-4, 1), "closed": "right"},
            0.25,
        ),
    ],
)
def test_s1_max(closed, kwargs, expected_val):
    from staircase.core import stats

    assert stats.max(s1(closed=closed), **kwargs) == expected_val


@pytest.mark.parametrize(
    "closed, kwargs, expected_val",
    [
        (
            "left",
            {},
            np.array([-1.75, -0.5, 0.0, 0.25, 2.0, 2.75]),
        ),
        (
            "left",
            {"where": (-4, 10)},
            np.array([-1.75, -0.5, 0.25, 2.0, 2.75]),
        ),
        (
            "left",
            {"where": (1, 6)},
            np.array([0.25, 2.0, 2.75]),
        ),
        (
            "right",
            {"where": (1, 6), "closed": "left"},
            np.array([-1.75, 0.25, 2.0, 2.75]),
        ),
        (
            "left",
            {"where": (1, 6), "closed": "right"},
            np.array([-0.5, 0.25, 2.0, 2.75]),
        ),
    ],
)
def test_s1_values_in_range(closed, kwargs, expected_val):
    assert np.array_equal(s1(closed=closed).values_in_range(**kwargs), expected_val)


@pytest.mark.parametrize(
    "x, kwargs, expected_val",
    [
        (
            [-4, -2, 1, 3],
            {"side": "right"},
            np.array([-1.75, -1.75, 0.25, 2.75]),
        ),
        (
            [-4, -2, 1, 3],
            {"side": "right"},
            np.array([-1.75, -1.75, 0.25, 2.75]),
        ),
        (
            [-4, -2, 1, 3],
            {"side": "left"},
            np.array([0.0, -1.75, -1.75, 0.25]),
        ),
    ],
)
def test_s1_sample(s1_fix, x, kwargs, expected_val):
    assert np.array_equal(s1_fix.limit(x, **kwargs), expected_val)


@pytest.mark.parametrize(
    "x, kwargs, expected_val",
    [
        (
            [-4, -2, 1, 3],
            {"aggfunc": "mean", "window": (-0.5, 0.5)},
            np.array([-0.875, -1.75, -0.75, 1.5]),
        ),
        (
            [-4, -2, 1, 3],
            {"aggfunc": "mean", "window": (-1, 0)},
            np.array([0.0, -1.75, -1.75, 0.25]),
        ),
        (
            [-4, -2, 1, 3],
            {"aggfunc": "mean", "window": (0, 1)},
            np.array([-1.75, -1.75, 0.25, 2.75]),
        ),
    ],
)
def test_s1_agg_mean(s1_fix, x, kwargs, expected_val):
    window = kwargs["window"]
    x = np.array(x)
    ii = pd.IntervalIndex.from_arrays(x + window[0], x + window[1])
    assert np.array_equal(s1_fix.slice(ii).mean().values, expected_val)


@pytest.mark.parametrize(
    "closed, x, kwargs, expected_val",
    [
        (
            "left",
            [0, 2, 7],
            {"aggfunc": "max", "window": (-1, 1)},
            np.array([-1.75, 0.25, -0.5]),
        ),
        (
            "right",
            [0, 2, 7],
            {"aggfunc": "max", "window": (-1, 1), "closed": "left"},
            np.array([-1.75, 0.25, 2.0]),
        ),
        (
            "left",
            [0, 2, 7],
            {"aggfunc": "max", "window": (-1, 1), "closed": "right"},
            np.array([0.25, 2.75, -0.5]),
        ),
        (
            "right",
            [0, 2, 7],
            {"aggfunc": "max", "window": (-1, 1), "closed": "right"},
            np.array([-1.75, 0.25, -0.5]),
        ),
    ],
)
def test_s1_agg_max(closed, x, kwargs, expected_val):
    window = kwargs["window"]
    x = np.array(x)
    ii = pd.IntervalIndex.from_arrays(
        x + window[0], x + window[1], closed=kwargs.get("closed", "left")
    )
    assert np.array_equal(s1(closed=closed).slice(ii).max().values, expected_val)


def test_plot(s1_fix):
    s1_fix.plot()


def test_add_1(s1_fix, s2_fix):
    assert pd.Series.equals(
        (s1_fix + s2_fix).step_changes,
        pd.Series(
            {
                -4: -1.75,
                -2: -1.75,
                1: 1.25,
                2: 4.5,
                2.5: -2.5,
                3: 2.5,
                4: 2.5,
                5: -5.25,
                6: -2.5,
                7: 2.5,
                8: 5,
                10: -4.5,
            }
        ),
    )


def test_add_2(s1_fix):
    s = s1_fix + 3
    assert s(float("-inf")) == 3
    assert pd.Series.equals(
        s.step_changes,
        s1_fix.step_changes,
    )


def test_divide(s1_fix, s2_fix):
    assert pd.Series.equals(
        (s1_fix / (s2_fix + 1)).step_changes,
        pd.Series(
            {
                -4: -1.75,
                -2: 4.083333333333334,
                1: -2.5,
                2: 0.25,
                2.5: 0.4166666666666667,
                3: 5.0,
                4: -4.583333333333333,
                5: -2.25,
                6: 1.6666666666666665,
                7: -0.8333333333333333,
                8: 0.4166666666666667,
                10: 0.08333333333333333,
            }
        ),
    )


def test_divide_scalar(s1_fix):
    assert pd.Series.equals(
        (s1_fix / 0.5).step_changes,
        pd.Series(
            {
                -4: -3.5,
                1: 4.0,
                3: 5.0,
                5: -1.5,
                6: -5.0,
                10: 1.0,
            }
        ),
    )


def test_multiply(s1_fix, s2_fix):
    assert pd.Series.equals(
        (s1_fix * s2_fix).step_changes,
        pd.Series(
            {
                -2: 3.0625,
                1: -3.6875,
                2: 1.125,
                2.5: -0.625,
                3: -1.25,
                4: 6.875,
                5: -10.5,
                6: 6.25,
                7: -1.25,
                8: -2.5,
                10: 2.5,
            }
        ),
    )


def test_multiply_scalar(s1_fix):
    assert pd.Series.equals(
        (s1_fix * 3).step_changes,
        pd.Series(
            {
                -4: -5.25,
                1: 6.0,
                3: 7.5,
                5: -2.25,
                6: -7.5,
                10: 1.5,
            }
        ),
    )


def test_eq_3():
    assert Stairs(initial_value=3) == 3


def test_ne_3(s1_fix):
    assert s1_fix != 3


def test_diff(s1_fix):
    assert pd.Series.equals(
        s1_fix.diff(1).step_changes,
        pd.Series(
            {
                -4: -1.75,
                -3: 1.75,
                1: 2,
                2: -2,
                3: 2.5,
                4: -2.5,
                5: -0.75,
                6: -1.75,
                7: 2.5,
                10: 0.5,
                11: -0.5,
            }
        ),
    )


def test_str(s1_fix):
    assert str(s1_fix) is not None
    assert str(s1_fix) != ""


def test_repr(s1_fix):
    assert repr(s1_fix) is not None
    assert repr(s1_fix) != ""


def test_make_test_data():
    assert type(test_data.make_test_data()) == pd.DataFrame
