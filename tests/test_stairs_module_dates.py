import pytest
import pandas as pd
import numpy as np
import staircase.stairs as stairs
from sortedcontainers import SortedSet

@pytest.fixture
def IS1():
    int_seq1 = stairs.Stairs(0, use_dates=True)
    int_seq1.layer(pd.Timestamp(2020,1,1),pd.Timestamp(2020,1,10),2)
    int_seq1.layer(pd.Timestamp(2020,1,3),pd.Timestamp(2020,1,5),2.5)
    int_seq1.layer(pd.Timestamp(2020,1,6),pd.Timestamp(2020,1,7),-2.5)
    int_seq1.layer(pd.Timestamp(2020,1,7),pd.Timestamp(2020,1,10),-2.5)
    return int_seq1

@pytest.fixture
def IS2():    
    int_seq2 = stairs.Stairs(0, use_dates=True)
    int_seq2.layer(pd.Timestamp(2020,1,1),pd.Timestamp(2020,1,7),-2.5)
    int_seq2.layer(pd.Timestamp(2020,1,8),pd.Timestamp(2020,1,10),5)
    int_seq2.layer(pd.Timestamp(2020,1,2),pd.Timestamp(2020,1,5),4.5)
    int_seq2.layer(pd.Timestamp(2020,1,2,12),pd.Timestamp(2020,1,4),-2.5)
    return int_seq2

def test_min_pair(IS1, IS2):
    assert stairs._min_pair(IS1,IS2).step_changes() == {pd.Timestamp('2020-01-01'): -2.5,
                                                        pd.Timestamp('2020-01-02'): 4.5,
                                                        pd.Timestamp('2020-01-02 12:00:00'): -2.5,
                                                        pd.Timestamp('2020-01-04'): 2.5,
                                                        pd.Timestamp('2020-01-05'): -4.5,
                                                        pd.Timestamp('2020-01-07'): 2.0,
                                                        pd.Timestamp('2020-01-10'): 0.5}

def test_max_pair(IS1, IS2):
    assert stairs._max_pair(IS1,IS2).step_changes() == {pd.Timestamp('2020-01-01'): 2.0,
                                                        pd.Timestamp('2020-01-03'): 2.5,
                                                        pd.Timestamp('2020-01-05'): -2.5,
                                                        pd.Timestamp('2020-01-06'): -2.5,
                                                        pd.Timestamp('2020-01-07'): 0.5,
                                                        pd.Timestamp('2020-01-08'): 5.0,
                                                        pd.Timestamp('2020-01-10'): -5.0}
    
def test_get_union_of_points_1(IS1, IS2):
    union = list(stairs._get_union_of_points({1:IS1, 2:IS2}))
    union.pop(0)
    assert stairs._convert_float_to_date(union) == [pd.Timestamp('2020-01-01'), pd.Timestamp('2020-01-02'),  pd.Timestamp('2020-01-02 12:00:00'),
                                                        pd.Timestamp('2020-01-03'), pd.Timestamp('2020-01-04'), pd.Timestamp('2020-01-05'),
                                                        pd.Timestamp('2020-01-06'), pd.Timestamp('2020-01-07'), pd.Timestamp('2020-01-08'), pd.Timestamp('2020-01-10')]

def test_get_union_of_points_2(IS1, IS2):
    union = list(stairs._get_union_of_points(pd.Series([IS1, IS2])))
    union.pop(0)
    assert stairs._convert_float_to_date(union) == [pd.Timestamp('2020-01-01'), pd.Timestamp('2020-01-02'),  pd.Timestamp('2020-01-02 12:00:00'),
                                                        pd.Timestamp('2020-01-03'), pd.Timestamp('2020-01-04'), pd.Timestamp('2020-01-05'),
                                                        pd.Timestamp('2020-01-06'), pd.Timestamp('2020-01-07'), pd.Timestamp('2020-01-08'), pd.Timestamp('2020-01-10')]

def test_get_union_of_points_3(IS1, IS2):
    union = list(stairs._get_union_of_points(np.array([IS1, IS2])))
    union.pop(0)
    assert stairs._convert_float_to_date(union) == [pd.Timestamp('2020-01-01'), pd.Timestamp('2020-01-02'),  pd.Timestamp('2020-01-02 12:00:00'),
                                                        pd.Timestamp('2020-01-03'), pd.Timestamp('2020-01-04'), pd.Timestamp('2020-01-05'),
                                                        pd.Timestamp('2020-01-06'), pd.Timestamp('2020-01-07'), pd.Timestamp('2020-01-08'), pd.Timestamp('2020-01-10')]

def test_get_union_of_points_4(IS1, IS2):
    union = list(stairs._get_union_of_points([IS1, IS2]))
    union.pop(0)
    assert stairs._convert_float_to_date(union) == [pd.Timestamp('2020-01-01'), pd.Timestamp('2020-01-02'),  pd.Timestamp('2020-01-02 12:00:00'),
                                                        pd.Timestamp('2020-01-03'), pd.Timestamp('2020-01-04'), pd.Timestamp('2020-01-05'),
                                                        pd.Timestamp('2020-01-06'), pd.Timestamp('2020-01-07'), pd.Timestamp('2020-01-08'), pd.Timestamp('2020-01-10')]

def test_get_union_of_points_5(IS1, IS2):
    union = list(stairs._get_union_of_points((IS1, IS2)))
    union.pop(0)
    assert stairs._convert_float_to_date(union) == [pd.Timestamp('2020-01-01'), pd.Timestamp('2020-01-02'),  pd.Timestamp('2020-01-02 12:00:00'),
                                                        pd.Timestamp('2020-01-03'), pd.Timestamp('2020-01-04'), pd.Timestamp('2020-01-05'),
                                                        pd.Timestamp('2020-01-06'), pd.Timestamp('2020-01-07'), pd.Timestamp('2020-01-08'), pd.Timestamp('2020-01-10')]

def test_using_dates_1(IS1, IS2):
    assert stairs._using_dates({1:IS1, 2:IS2})
    
def test_using_dates_2(IS1, IS2):
    assert stairs._using_dates(pd.Series([IS1, IS2]))

def test_using_dates_3(IS1, IS2):
    assert stairs._using_dates(np.array([IS1, IS2]))

def test_using_dates_4(IS1, IS2):
    assert stairs._using_dates([IS1, IS2])

def test_using_dates_5(IS1, IS2):
    assert stairs._using_dates((IS1, IS2))
    
def test_aggregate_1(IS1, IS2):
    assert stairs.aggregate({1:IS1, 2:IS2}, np.mean).step_changes() == {pd.Timestamp('2020-01-01'): -0.25, pd.Timestamp('2020-01-02'): 2.25, pd.Timestamp('2020-01-02 12:00:00'): -1.25,
                                                                         pd.Timestamp('2020-01-03'): 1.25, pd.Timestamp('2020-01-04'): 1.25, pd.Timestamp('2020-01-05'): -3.5,
                                                                         pd.Timestamp('2020-01-06'): -1.25, pd.Timestamp('2020-01-07'): 1.25, pd.Timestamp('2020-01-08'): 2.5,
                                                                         pd.Timestamp('2020-01-10'): -2.25}

def test_aggregate_2(IS1, IS2):
    assert stairs.aggregate(pd.Series([IS1, IS2]), np.mean).step_changes() == {pd.Timestamp('2020-01-01'): -0.25, pd.Timestamp('2020-01-02'): 2.25, pd.Timestamp('2020-01-02 12:00:00'): -1.25,
                                                                         pd.Timestamp('2020-01-03'): 1.25, pd.Timestamp('2020-01-04'): 1.25, pd.Timestamp('2020-01-05'): -3.5,
                                                                         pd.Timestamp('2020-01-06'): -1.25, pd.Timestamp('2020-01-07'): 1.25, pd.Timestamp('2020-01-08'): 2.5,
                                                                         pd.Timestamp('2020-01-10'): -2.25}

def test_aggregate_3(IS1, IS2):
    assert stairs.aggregate(np.array([IS1, IS2]), np.mean).step_changes() == {pd.Timestamp('2020-01-01'): -0.25, pd.Timestamp('2020-01-02'): 2.25, pd.Timestamp('2020-01-02 12:00:00'): -1.25,
                                                                         pd.Timestamp('2020-01-03'): 1.25, pd.Timestamp('2020-01-04'): 1.25, pd.Timestamp('2020-01-05'): -3.5,
                                                                         pd.Timestamp('2020-01-06'): -1.25, pd.Timestamp('2020-01-07'): 1.25, pd.Timestamp('2020-01-08'): 2.5,
                                                                         pd.Timestamp('2020-01-10'): -2.25}

def test_aggregate_4(IS1, IS2):
    assert stairs.aggregate([IS1, IS2], np.mean).step_changes() == {pd.Timestamp('2020-01-01'): -0.25, pd.Timestamp('2020-01-02'): 2.25, pd.Timestamp('2020-01-02 12:00:00'): -1.25,
                                                                         pd.Timestamp('2020-01-03'): 1.25, pd.Timestamp('2020-01-04'): 1.25, pd.Timestamp('2020-01-05'): -3.5,
                                                                         pd.Timestamp('2020-01-06'): -1.25, pd.Timestamp('2020-01-07'): 1.25, pd.Timestamp('2020-01-08'): 2.5,
                                                                         pd.Timestamp('2020-01-10'): -2.25}

def test_aggregate_5(IS1, IS2):
    assert stairs.aggregate((IS1, IS2), np.mean).step_changes() == {pd.Timestamp('2020-01-01'): -0.25, pd.Timestamp('2020-01-02'): 2.25, pd.Timestamp('2020-01-02 12:00:00'): -1.25,
                                                                         pd.Timestamp('2020-01-03'): 1.25, pd.Timestamp('2020-01-04'): 1.25, pd.Timestamp('2020-01-05'): -3.5,
                                                                         pd.Timestamp('2020-01-06'): -1.25, pd.Timestamp('2020-01-07'): 1.25, pd.Timestamp('2020-01-08'): 2.5,
                                                                         pd.Timestamp('2020-01-10'): -2.25}
                                                                         
                                                                    
def test_aggregate_6(IS1, IS2):
    assert stairs.aggregate(
    {1:IS1, 2:IS2}, 
    np.mean, 
    [pd.Timestamp(2020,1,3),pd.Timestamp(2020,1,5), pd.Timestamp(2020,1,7),pd.Timestamp(2020,1,9)]
    ).step_changes() == {pd.Timestamp('2020-01-03'): 2.0,
                         pd.Timestamp('2020-01-05'): -2.25,
                         pd.Timestamp('2020-01-09'): 2.5}
def test_aggregate_7(IS1, IS2):
    assert stairs.aggregate(
    pd.Series([IS1, IS2]), 
    np.mean, 
    [pd.Timestamp(2020,1,3),pd.Timestamp(2020,1,5), pd.Timestamp(2020,1,7),pd.Timestamp(2020,1,9)]
    ).step_changes() == {pd.Timestamp('2020-01-03'): 2.0,
                         pd.Timestamp('2020-01-05'): -2.25,
                         pd.Timestamp('2020-01-09'): 2.5}

def test_aggregate_8(IS1, IS2):
    assert stairs.aggregate(
    np.array([IS1, IS2]), 
    np.mean, 
    [pd.Timestamp(2020,1,3),pd.Timestamp(2020,1,5), pd.Timestamp(2020,1,7),pd.Timestamp(2020,1,9)]
    ).step_changes() == {pd.Timestamp('2020-01-03'): 2.0,
                         pd.Timestamp('2020-01-05'): -2.25,
                         pd.Timestamp('2020-01-09'): 2.5}


def test_aggregate_9(IS1, IS2):
    assert stairs.aggregate(
    [IS1, IS2], 
    np.mean, 
    [pd.Timestamp(2020,1,3),pd.Timestamp(2020,1,5), pd.Timestamp(2020,1,7),pd.Timestamp(2020,1,9)]
    ).step_changes() == {pd.Timestamp('2020-01-03'): 2.0,
                         pd.Timestamp('2020-01-05'): -2.25,
                         pd.Timestamp('2020-01-09'): 2.5}

def test_aggregate_10(IS1, IS2):
    assert stairs.aggregate(
    (IS1, IS2), 
    np.mean, 
    [pd.Timestamp(2020,1,3),pd.Timestamp(2020,1,5), pd.Timestamp(2020,1,7),pd.Timestamp(2020,1,9)]
    ).step_changes() == {pd.Timestamp('2020-01-03'): 2.0,
                         pd.Timestamp('2020-01-05'): -2.25,
                         pd.Timestamp('2020-01-09'): 2.5}
                         

# def test_sample_1(IS1, IS2):
    # sample = stairs.sample(pd.Series([IS1, IS2]))
    # points=[float('-inf'), -4.0, -2.0, 1.0, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, float('-inf'), -4.0, -2.0, 1.0, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0]
    # key=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    # value=[0.0, -1.75, -1.75, 0.25, 0.25, 0.25, 2.75, 2.75, 2.0, -0.5, -0.5, -0.5, 0.0, 0.0, 0.0, -1.75, -2.5, 2.0, -0.5, -0.5, 2.0, -2.5, -2.5, 0.0, 5.0, 0.0]
    # assert sample.eq(pd.DataFrame({"points":points, "key":key, "value":value})).all(axis=None)
    
# def test_sample_2(IS1, IS2):
    # sample = stairs.sample({0:IS1, 1:IS2})
    # points=[float('-inf'), -4.0, -2.0, 1.0, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, float('-inf'), -4.0, -2.0, 1.0, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0]
    # key=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    # value=[0.0, -1.75, -1.75, 0.25, 0.25, 0.25, 2.75, 2.75, 2.0, -0.5, -0.5, -0.5, 0.0, 0.0, 0.0, -1.75, -2.5, 2.0, -0.5, -0.5, 2.0, -2.5, -2.5, 0.0, 5.0, 0.0]
    # assert sample.eq(pd.DataFrame({"points":points, "key":key, "value":value})).all(axis=None)
    
# def test_sample_3(IS1, IS2):
    # sample = stairs.sample(pd.Series([IS1, IS2]), how='left')    
    # points=[float('-inf'), -4.0, -2.0, 1.0, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, float('-inf'), -4.0, -2.0, 1.0, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0]
    # key=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    # value=[0.0, 0.0, -1.75, -1.75, 0.25, 0.25, 0.25, 2.75, 2.75, 2.0, -0.5, -0.5, -0.5, 0.0, 0.0, 0.0, -1.75, -2.5, 2.0, -0.5, -0.5, 2.0, -2.5, -2.5, 0.0, 5.0]
    # assert sample.eq(pd.DataFrame({"points":points, "key":key, "value":value})).all(axis=None)
    
# def test_sample_4(IS1, IS2):
    # sample = stairs.sample({0:IS1, 1:IS2}, how='left')    
    # points=[float('-inf'), -4.0, -2.0, 1.0, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, float('-inf'), -4.0, -2.0, 1.0, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0]
    # key=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    # value=[0.0, 0.0, -1.75, -1.75, 0.25, 0.25, 0.25, 2.75, 2.75, 2.0, -0.5, -0.5, -0.5, 0.0, 0.0, 0.0, -1.75, -2.5, 2.0, -0.5, -0.5, 2.0, -2.5, -2.5, 0.0, 5.0]
    # assert sample.eq(pd.DataFrame({"points":points, "key":key, "value":value})).all(axis=None)
    
# def test_sample_5(IS1, IS2):
    # sample = stairs.sample(pd.Series([IS1, IS2]), 3)
    # points = [3, 3]
    # key = [0, 1]
    # value = [2.75, -0.5]
    # assert sample.eq(pd.DataFrame({"points":points, "key":key, "value":value})).all(axis=None)
    
# def test_sample_6(IS1, IS2):
    # sample = stairs.sample({0:IS1, 1:IS2}, 3)
    # points = [3, 3]
    # key = [0, 1]
    # value = [2.75, -0.5]
    # assert sample.eq(pd.DataFrame({"points":points, "key":key, "value":value})).all(axis=None)
    
# def test_sample_7(IS1, IS2):
    # sample = stairs.sample(pd.Series([IS1, IS2]), 3, how='left')    
    # points = [3, 3]
    # key = [0, 1]
    # value = [0.25, -0.5]
    # assert sample.eq(pd.DataFrame({"points":points, "key":key, "value":value})).all(axis=None)
    
# def test_sample_8(IS1, IS2):
    # sample = stairs.sample({0:IS1, 1:IS2}, 3, how='left')    
    # points = [3, 3]
    # key = [0, 1]
    # value = [0.25, -0.5]
    # assert sample.eq(pd.DataFrame({"points":points, "key":key, "value":value})).all(axis=None)
    
# def test_sample_9(IS1, IS2):
    # sample = stairs.sample(pd.Series([IS1, IS2]), [3, 6, 8])
    # points = [3, 6, 8, 3, 6, 8]
    # key = [0, 0, 0, 1, 1, 1]
    # value = [2.75, -0.5, -0.5, -0.5, -2.5, 5.0]
    # assert sample.eq(pd.DataFrame({"points":points, "key":key, "value":value})).all(axis=None)
    
# def test_sample_10(IS1, IS2):
    # sample = stairs.sample({0:IS1, 1:IS2}, [3, 6, 8])
    # points = [3, 6, 8, 3, 6, 8]
    # key = [0, 0, 0, 1, 1, 1]
    # value = [2.75, -0.5, -0.5, -0.5, -2.5, 5.0]
    # assert sample.eq(pd.DataFrame({"points":points, "key":key, "value":value})).all(axis=None)
    
# def test_sample_11(IS1, IS2):
    # sample = stairs.sample(pd.Series([IS1, IS2]), [3, 6, 8], how='left')    
    # points = [3, 6, 8, 3, 6, 8]
    # key = [0, 0, 0, 1, 1, 1]
    # value = [0.25, 2.0, -0.5, -0.5, -2.5, 0.0]
    # assert sample.eq(pd.DataFrame({"points":points, "key":key, "value":value})).all(axis=None)
    
# def test_sample_12(IS1, IS2):
    # sample = stairs.sample({0:IS1, 1:IS2}, [3, 6, 8], how='left')    
    # points = [3, 6, 8, 3, 6, 8]
    # key = [0, 0, 0, 1, 1, 1]
    # value = [0.25, 2.0, -0.5, -0.5, -2.5, 0.0]
    # assert sample.eq(pd.DataFrame({"points":points, "key":key, "value":value})).all(axis=None)
    
    