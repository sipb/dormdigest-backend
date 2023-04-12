def list_dict_convert(query_res_lst, nested=False,remove_sql_ref=True,):
    '''
    Given a list which contains query results from SQLalchemy,
    return a list of their Python dictionary representation
    
    If `remove_sql_ref` set to True, the `_sa_instance_state`
    key automatically inserted by SQLalchemy will be removed 
    from each list entry
    
    If `nested` set to True, function will assume each item
    in list is a tuple of models and will unpack them separately
    
    Safety: For value safety this function gets the shallow copy
    of each entry's dictionary representation
    
    Source: https://stackoverflow.com/questions/1958219/how-to-convert-sqlalchemy-row-object-to-a-python-dict
    '''
    if remove_sql_ref:
        converted_lst = []
        for entry in query_res_lst:
            if nested:
                entry_lst = [] #To be converted back into tuple later
                for model in entry:
                    model_dict = model.__dict__.copy()
                    model_dict.pop('_sa_instance_state')
                    entry_lst.append(model_dict)
                converted_lst.append(tuple(entry_lst))
            else: 
                entry_dict = entry.__dict__.copy()
                entry_dict.pop('_sa_instance_state')
                converted_lst.append(entry_dict)
        return converted_lst
    else:
        return [r.__dict__.copy() for r in query_res_lst]

def check_object_params(target_dict,req_params):
    '''
    Check if a given dictionary has all of the keys defined in req_params (lst)
    
    Parameters
    ----------
    target_dict : dict
    req_params : list of str
        Defines the keys that we want to require/check for in target_dict
    '''
    res = True
    for param in req_params:
        if param not in target_dict:
            res = False
    return res
