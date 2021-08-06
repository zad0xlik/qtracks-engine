import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
import time
from functools import reduce


def create_pivot_table(df, pivot_dimensions, pricing_dimensions, continuous_variables):
    
    """
    How does this work?
    
    continuous_variables    = [A B]
    pricing_dimensions      = [C:{c1 c2}, D={d1 d2}]
    df.dim_key              = [c1;d1 c1;d2 c2;d1 c2;d2]
    df.dim                  = it = 1 -> A;c1;d1 A;c1;d2 A;c2;d1 A;c2;d2 |  it = 2 => B;c1;d1 B;c1;d2 B;c2;d1 B;c2;d2 pivot_dimensions [E:{e1 e2}]
    output                  = rows: e1, e2 | cols: | A;c1;d1 A;c1;d2 A;c2;d1 A;c2d2 | B;c1;d1 B;c1;d2 B;c2;d1 B;c2d2
    pivot_table             = aggregates the values of 'series' on the output table
    """
    start = time.time()
    print('running create_pivot_table..')
    
    if len(continuous_variables) == 0 or len(pricing_dimensions) == 0 or len(pivot_dimensions) == 0:
        raise ValueError('One of the input variable lists is empty!')
        
    df['dim_key'] = df[pricing_dimensions].apply(lambda x: ';'.join(x), axis=1)
    
    result = []
    for series in continuous_variables: 
        df['dim'] = series + ';'+ df['dim_key']
        result.append(df.pivot_table(values=series, index=pivot_dimensions, columns='dim', aggfunc=np.mean))
        
    output = result[0]
    if len(continuous_variables) > 1:
        output = output.join(result[1:], how='outer')
        
    end = time.time()
    print('time: ',"{0:.2f}".format(end - start))
    return output


def get_neighbors_clusters_for_depth(df, depth):
    
    cols                = df.columns.tolist()
    neighbor_clusters   = dict()
    visited             = dict()
    counter             = 0
    
    # find all neighbor clusters of depth=depth for each col_i
    for col_i in cols:
        if col_i not in visited:
            visited[col_i] = True
            dims = col_i.split(';')
            if (depth >= len(dims) - 1):
                raise ValueError('Depth is too large for this column name: ', col_i)
            dims = dims[:-depth]
            neighbors_list = []
            # search in the column list to find the neighbors col_j of col_i
            for col_j in cols:
                if col_j.split(';')[:-depth] == dims:
                    neighbors_list.append(col_j)
                    visited[col_j] = True
            neighbor_clusters[counter] = neighbors_list   
            counter += 1
    
    # neighbors[0]:['A', B','C','D'] => the neighbor cluster of column A, B, C, D
    return neighbor_clusters


def get_neighbor_clusters_for_all_depths(df, max_depth):
    
    neighbor_cluster_list = []
    for i in range(max_depth):
        neighbor_cluster_list.append(get_neighbors_clusters_for_depth(df, i+1))
    return neighbor_cluster_list


def print_neighbor_clusters_stats(df, neighbor_cluster_list):
    
    # print the stats
    print('max_depth = len(neighbor_cluster_list) : ', len(neighbor_cluster_list))
    for depth in range(len(neighbor_cluster_list)):
        print('depth= ', depth + 1)
        max_clustersize, min_clustersize = 0, df.shape[1] + 1
        for clus in range(len(neighbor_cluster_list[depth])):
            min_clustersize = min(min_clustersize, len(neighbor_cluster_list[depth][clus]))
            max_clustersize = max(max_clustersize, len(neighbor_cluster_list[depth][clus]))
        print('min_clustersize: ', min_clustersize)
        print('max_clustersize: ', max_clustersize)

    # print a sample results
    #print('\nsample results: ', neighbor_cluster_list[0][0])
    #print('\nsample results: ', neighbor_cluster_list[1][2]);    
    
    
def run_bfs_for_depth(df, neighbor_cluster_list, depth, debug_verbose=False):
    
    """
    This function runs a BFS traversal on the neighbor tree for level = depth. 
    i.e. if depth = 1, it only uses depth-1 neighbor information to impute the NaN values
    The full process should run through all depths, from 1 to max_depth to complete the imputation.
    """
    if not neighbor_cluster_list or len(neighbor_cluster_list) == 0:
        raise ValueError('Invalud input: the given neighbor_cluster_list is Null or Empty!')
    
    if (depth > len(neighbor_cluster_list) or depth == 0):
        raise ValueError('Invalud input: the valid range of depth is: 1 to ' + str(len(neighbor_cluster_list)))     
        
    print('- run_bfs_for_depth : ' + str(depth))
    print('-- n clusters: ' + str(len(neighbor_cluster_list[depth-1])))

    count_test = 0
    df_ans = pd.DataFrame()
    for i in range(len(neighbor_cluster_list[depth-1])):
        
        if i % 500 == 0: print('-- cluster id : ' + str(i))
        col_list    = neighbor_cluster_list[depth-1][i]
        df_         = df[col_list]
        df_mean     = df_.mean(axis=1, skipna=True)
        df_nan      = df_.isna().applymap(lambda x: int(x))
        df_add      = df_nan.mul(df_mean, axis=0)
        df_base     = df_.fillna(0)
        df_res      = df_base + df_add
        df_ans      = df_res if i == 0 else pd.concat([df_ans,df_res], axis=1)
            
        if debug_verbose:    
            print(i, col_list)
            print('\n')
            print(df_.head())
            print('df_mean: '   , df_mean.head())
            print('df_nan: '    , df_nan.head())
            print('df_add: '    , df_add.head())
            print('df_base: '   , df_base.head())
            print('df_res: '    , df_res.head())
            print(df_res.columns)
            print(df_ans.columns)
            count_test += 1
            if(count_test > 0): break
            
    return df_ans
    
    
def run_bfs_for_all_depths(df, neighbor_cluster_list, max_depth, debug_verbose=False):
    
    if (max_depth > len(neighbor_cluster_list) or max_depth == 0):
        raise ValueError('Invalud input: the valid range of max_depth is: 1 to ' + str(len(neighbor_cluster_list))) 
        
    for i in range(max_depth):
        df = run_bfs_for_depth(df, neighbor_cluster_list, depth=i+1, debug_verbose=debug_verbose)
        
    return df

def impute_pivot_table_nearest_neighbors(df_pivot, max_depth=4, verbose=False):
    
    start = time.time()
    print('running impute_pivot_table_nearest_neighbors..')
    
    # print inputs
    print('Input DataFrame:')
    print('df_pivot.shape: ', df_pivot.shape)
    print('Null Counts: ', df_pivot.isnull().sum().sum())
    
    # find the neighbor clusters first for each depth
    neighbor_cluster_list = get_neighbor_clusters_for_all_depths(df_pivot, max_depth)
    
    # print neighbor clusters info
    if verbose:
        print_neighbor_clusters_stats(df_pivot, neighbor_cluster_list)
    
    # run BFS on all depth values
    df_pivot_imputed = run_bfs_for_all_depths(df_pivot, neighbor_cluster_list, max_depth, debug_verbose=False)
    
    # print results
    print('Output DataFrame:')
    print('df_pivot_imputer.shape: ', df_pivot_imputed.shape)
    print('Null Counts: ', df_pivot_imputed.isnull().sum().sum())
    
    end = time.time()
    print('time: ',"{0:.2f}".format(end - start))
    
    return df_pivot_imputed


def rolling_window_calc(df_input, win_size= 6, min_periods=1, verbose= False, plotting=False):
    
    """
    win_size :: number of months to run the rolling average
    min_periods :: 
    
    """
    start = time.time()
    print('running rolling_window_calc..')
    
    cols = df_input.columns.tolist()
    df = pd.DataFrame()
    df_output = pd.DataFrame()
    
    if verbose: print('processing ' + str(df_input.shape[1]) + ' columns.'); print('col number: '); count = 0;
    for col in cols:
        count += 1
        if verbose and count % 500 == 0: print('col ' + str(count) + ' col_name: ' + str(col))
        
        # Normalize the data    
        A = np.nanmin(df_input[col], axis=0)
        B = np.nanmax(df_input[col], axis=0)-np.nanmin(df_input[col], axis=0)
        y = (df_input[col] - A) / B if B > 0 else df_input[col]        
        df['data'] = y
        df['mean'] = y.rolling(win_size, min_periods).mean()
        # df['std'] = y.rolling(win_size, min_periods=1).std()
        # df['median'] = y.rolling(win_size, min_periods=1).median()
        
        # De-Normalize the data
        df_output[col] = A + (df['mean'] * B) if B > 0 else df['mean']
        
        if plotting:
            x = np.arange(len(y))
            plt.plot(x,df['data'], 'lightgray', label='data'); 
            plt.plot(x,df['mean'], 'green', label='rolling mean');
            #plt.plot(x,df['median'], 'red', label='rolling median');
            #plt.plot(x,df['std'], 'lightblue', label='rolling std');

    if verbose:
        print('Input DataFrame:')
        print('- shape: ', df_input.shape)
        print('- Null Counts: ', df_input.isnull().sum().sum())
        print('Output DataFrame:')
        print('- shape: ', df_output.shape)
        print('- Null Counts: ', df_output.isnull().sum().sum())

    end = time.time()
    print('time: ', "{0:.2f}".format(end - start))
    
    return df_output


def interpolate_missing_values(df_input, ip_method='linear', ip_limit=14, ip_axis=0, verbose=False):
    """
    ip_method :: ‘linear’: Ignore the index and treat the values as equally spaced.
    ip_limit :: Maximum number of consecutive NaNs to fill. Must be greater than 0.
    """
    start = time.time()
    print('running interpolate_missing_values..')
    
    df_output = df_input.interpolate(method=ip_method, limit=ip_limit, axis=ip_axis)
    
    # print results
    if verbose:
        print('Input DataFrame:')
        print('- shape: ', df_input.shape)
        print('- Null Counts: ', df_input.isnull().sum().sum())        
        print('Output DataFrame:')
        print('- shape: ', df_output.shape)
        print('- Null Counts: ', df_output.isnull().sum().sum())        

    end = time.time()
    print('time: ', "{0:.2f}".format(end - start))
    
    return df_output


def savgol_filter_smoothing(df_input, sg_window_length, sg_polyorder, sg_mode='nearest', verbose=False):
    """
    ip_method :: ‘linear’: Ignore the index and treat the values as equally spaced.
    ip_limit :: Maximum number of consecutive NaNs to fill. Must be greater than 0.
    """ 
    start = time.time()
    print('running savgol_filter_smoothing..')
    
    cols = df_input.columns.tolist()
    df_output = df_input.copy(deep=True)
    
    for col in cols:
        
        y_input = np.array(df_output[col])
        y_smooth = savgol_filter(y_input, window_length= sg_window_length, polyorder= sg_polyorder, mode= sg_mode)
        
        # Make sure smoothing process doesn't add more missing values: if it does, then overwrite the NaN from input data
        if np.count_nonzero(~np.isnan(y_input)) > np.count_nonzero(~np.isnan(y_smooth)):
            #print(np.count_nonzero(np.isnan(y_input)), np.count_nonzero(np.isnan(y_smooth)))
            not_null_y = pd.Series(list(map(int, ~np.isnan(y_input))))
            null_ysmooth = pd.Series(list(map(int, np.isnan(y_smooth))))
            mask_list = not_null_y * null_ysmooth
            y_add = mask_list * y_input
            y_smooth_filled = np.nan_to_num(y_smooth)
            #print(y_smooth)
            y_smooth = np.array(y_smooth_filled + y_add)
            #print(y_smooth)
            #break
            #print(np.count_nonzero(np.isnan(y_input)), np.count_nonzero(np.isnan(y_smooth)),'\n')
        
        df_output[col] = y_smooth
        #print(df_output[col].isnull().sum())
    
    # print results
    if verbose:
        print('Input DataFrame:')
        print('- shape: ', df_input.shape)
        print('- Null Counts: ', df_input.isnull().sum().sum())        
        print('Output DataFrame:')
        print('- shape: ', df_output.shape)
        print('- Null Counts: ', df_output.isnull().sum().sum())   
    
    end = time.time()
    print('time: ',"{0:.2f}".format(end - start))
    
    return df_output
        
    
def impute_first_last_row(df_input, verbose=False):
    
    """
    Interpolation can't handle the first and last rows because there is no interval around them. 
    We can impute these two rows using the second and second last rows, if data is available. 
    """
    start = time.time()
    print('running impute_first_last_row..')
    
    cols = df_input.columns.tolist()
    n = df_input.shape[0]
    df_output = df_input.copy(deep=True)
    
    for col in cols:
        y = df_input[col].copy(deep=True)
        if np.isnan(y.iloc[0]): # and (~np.isnan(y_input.iloc[1])):
            y.iloc[0] = y.iloc[1]
        if np.isnan(y.iloc[n-1]): # and (~np.isnan(y_input.iloc[n-2]))):
            y.iloc[n-1] = y.iloc[n-2]
        df_output[col] = y
   
    if verbose:
        print('Input DataFrame:')
        print('- shape: ', df_input.shape)
        print('- Null Counts: ', df_input.isnull().sum().sum())        
        print('Output DataFrame:')
        print('- shape: ', df_output.shape)
        print('- Null Counts: ', df_output.isnull().sum().sum())   
    
    end = time.time()
    print('time: ',"{0:.2f}".format(end - start))  
    
    return df_output


def depivot_data_to_raw_format(df_original, df_pivot, pricing_dimensions, pivot_dimensions, continuous_variables, string_delimeter=';'):

    """

    :param df_original:
    :param df_pivot:
    :param pricing_dimensions:
    :param pivot_dimensions:
    :param continuous_variables:
    :return:
    """

    # # melt the pivot dataframe and add time as a column
    # df_ = df_pivot.copy(deep=True)
    # date_column = df_.reset_index()['snapshot_date']
    # date_all = pd.concat([date_column for _ in range(df_.shape[1])], ignore_index=True)
    # df_tmp = pd.melt(df_, id_vars='snapshot_date', value_vars=df_.columns).drop('snapshot_date', axis=1)
    # df_tmp['snapshot_date'] = date_all
    #
    # # split the pricing cells and convert dimensions back to columns
    # df_expand = df_tmp['variable'].str.split(";", expand=True)
    # cols = pricing_dimensions.copy()
    # cols.insert(0, 'var_type')
    # df_expand.columns = cols
    # df_expand['value'] = df_tmp['value']
    # df_expand['snapshot_date'] = df_tmp['snapshot_date']
    # df_expand.head()


    # melt the pivot dataframe and add time as a column
    df_ = df_pivot.copy(deep=True)
    series_column = df_.reset_index()[pivot_dimensions]
    series_all = pd.concat([series_column for _ in range(df_.shape[1])], ignore_index=True)


    # id_vars will need to be an ambiguous column name that needs to be dynamically updated
    df_tmp = pd.melt(df_, id_vars=pivot_dimensions[0], value_vars=df_.columns).drop(pivot_dimensions, axis=1)

    df_tmp[pivot_dimensions] = series_all

    # split the pricing cells and convert dimensions back to columns
    # df_expand = df_tmp['variable'].str.split(string_delimeter, expand=True)
    df_expand = df_tmp['dim'].str.split(string_delimeter, expand=True)
    cols = pricing_dimensions.copy()
    cols.insert(0, 'var_type')
    df_expand.columns = cols
    df_expand['value'] = df_tmp['value']
    df_expand[pivot_dimensions] = df_tmp[pivot_dimensions]
    df_expand.head()

    # create a data frame for each continue dimension
    df_sep = []

    for col in continuous_variables:
        df_sep.append(df_expand[df_expand['var_type'] == col])

    for ind in range(len(continuous_variables)):
        col_name = df_sep[ind]['var_type'].unique()[0]
        df_sep[ind].rename(index=str, columns={"value": col_name}, inplace=True)
        df_sep[ind].drop('var_type', axis=1, inplace=True)

    # join all data frames into one
    df_depivot = reduce(lambda left, right: pd.merge(left, right, on=pricing_dimensions + pivot_dimensions, how='outer'), df_sep)

    # return the final data frame
    df_original_groupby = df_original.groupby(pricing_dimensions + pivot_dimensions).mean().reset_index()
    print('Shape of original data (grouped by pricing_dimensions+pivot_dimensions): ', df_original_groupby.shape)
    print('Shape of preprocessed data: ', df_depivot.shape)
    print('Number of Nulls for continous variable of the original data : ',
          df_original_groupby[continuous_variables].isnull().sum().sum())
    print('Number of Nulls for continous variable of the preprocessed data : ',
          df_depivot[continuous_variables].isnull().sum().sum())

    return df_depivot
