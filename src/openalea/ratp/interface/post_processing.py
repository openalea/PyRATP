#       File author(s): Christian Fournier <Christian.Fournier@supagro.inra.fr>


""" post processing of RATP output
"""
import numpy
import pandas


def _process_light(df):
    w = df['area'] / df['agg_area']
    a_agg = df['agg_area'].values[0]
    res = pandas.Series(
        {'VegetationType': df['VegetationType'].values[0],
         'day': df['day'].values[0],
         'hour': df['hour'].values[0],
         'ShadedPAR': numpy.sum(df['ShadedPAR'] * w),
         # weighted mean of voxel values (weigth = primitive area)
         'SunlitPAR': numpy.sum(df['SunlitPAR'] * w),
         'ShadedArea': numpy.sum(
             df['ShadedArea'] / df['Area'] * w) * a_agg,
         # weighted mean of shaded fraction times shape_area
         'SunlitArea': numpy.sum(
             df['SunlitArea'] / df['Area'] * w) * a_agg,
         'Area': a_agg,
         'PAR': numpy.sum(df['PAR'] * w)})
    return res


def aggregate_light(dfvox, grid_map, scene_map, temporal=True):
    """  Aggregate ratp light outputs along scene inputs

    Args:
        dfvox: a pandas data frame with ratp.do_irradiation outputs
        grid_map: a 4-columns pandas dataframe mapping scene point_id to grid
         indices (jx, jy, jz)
        scene_map: a 2 or 3-columns pandas dataframe mapping scene point_id to
        point area and to an optional user-defined aggregation column. If 2
         columns only are given , results are given per point_id
        temporal: should iterations be aggregated ?

    Returns:
        a pandas dataframe with aggregated outputs

    """
    dfmap = pandas.merge(scene_map, grid_map)

    if len(scene_map.columns) == 2:
        aggregator = 'point_id'
        res = pandas.merge(dfmap, dfvox).loc[:, (
            'Iteration', 'point_id', 'area', 'PAR', 'ShadedArea', 'ShadedPAR',
            'SunlitArea', 'SunlitPAR', 'VegetationType', 'day', 'hour')]
        res = res.rename(columns={'area': 'Area'})

    else:
        aggregator = set(scene_map.columns).difference(
            ('point_id', 'area')).pop()
        aggregated_area = dfmap.loc[:, (aggregator, 'area')].groupby(
            aggregator).agg('sum').reset_index()
        aggregated_area = aggregated_area.rename(columns={'area': 'agg_area'})
        output = pandas.merge(pandas.merge(dfmap, aggregated_area), dfvox)
        grouped = output.groupby(['Iteration', aggregator])
        res = grouped.apply(_process_light).reset_index()

    if temporal and len(set(res['Iteration'])) > 1:
        grouped = res.groupby(aggregator)
        how = {'VegetationType': numpy.mean, 'day': numpy.mean,
               'hour': numpy.mean,
               'ShadedPAR': numpy.sum, 'SunlitPAR': numpy.sum,
               'ShadedArea': numpy.mean, 'SunlitArea': numpy.mean,
               'Area': numpy.mean, 'PAR': numpy.sum}
        res = grouped.agg(how).reset_index()

    return res


def aggregate_grid(dfvox, grid_map, area_map, by=('jx', 'jy'), temporal=True):
    """  Aggregate ratp light outputs along scene inputs

    Args:
        dfvox: a pandas data frame with ratp.do_irradiation outputs
        grid_map: a 4-columns pandas dataframe mapping scene point_id to grid
         indices (jx, jy, jz)
        area_map: a 2 columns pandas dataframe mapping scene point_id to
         point area
        by: a tuple naming cell dimension to aggregate on.
        temporal: should iterations be aggregated ?

    Returns:
        a pandas dataframe with aggregated outputs

    """
    dfmap = pandas.merge(area_map, grid_map)
    cols = [w for w in by] + ['area']
    aggregated_area = dfmap.loc[:,cols].groupby(
        by).agg('sum').reset_index().rename(columns={'area': 'agg_area'})
    output = pandas.merge(pandas.merge(dfmap, aggregated_area), dfvox)
    on = [w for w in by] + ['Iteration']
    grouped = output.groupby(on)
    res = grouped.apply(_process_light).reset_index()
    if temporal and len(set(res['Iteration'])) > 1:
        grouped = res.groupby(by)
        how = {'VegetationType': numpy.mean, 'day': numpy.mean,
               'hour': numpy.mean,
               'ShadedPAR': numpy.sum, 'SunlitPAR': numpy.sum,
               'ShadedArea': numpy.mean, 'SunlitArea': numpy.mean,
               'Area': numpy.mean, 'PAR': numpy.sum}
        res = grouped.agg(how).reset_index()

    return res
