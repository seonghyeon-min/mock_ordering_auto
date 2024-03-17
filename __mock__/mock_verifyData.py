import inspect
import mock_ordering
import pandas as pd
import numpy as np
import time
from random import random

PLATFORM_CODE = 'S23Y'

def set_verification_data() :
    mock_lst = []
    _country_lst = ['USA', 'KOREA', 'RUSSIA', 'JAPAN', 'UNITED KINGDOM']

    for idx in range(len(_country_lst)) : # country == 5
        for jdx in range(10) : # cp == 10
            if jdx < 5 : 
                mock_lst.append([_country_lst[idx], 'HOME', round(random(),2), round(random(),2)])
            else :
                mock_lst.append([_country_lst[idx], 'PREMIUM', round(random(),2), round(random(),2)])


    print(f'{time.ctime()} [{inspect.stack()[0].function}] {mock_lst}')

    return mock_lst

def get_CountryLst(data) :
    _countryLst = data['COUNTRY'].unique()
    print(f'{time.ctime()} [{inspect.stack()[0].function}] getCountries : {_countryLst}')

    return _countryLst

def data_vaildation(validation_mock_data) :
    _pobject = validation_mock_data
    _dataframe = pd.DataFrame(_pobject, columns=['COUNTRY', 'AREA', 'CP', 'CP_ID'])

    if _dataframe.empty :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] ErrorDataFrame')


    cntryLst = get_CountryLst(_dataframe)
    _original_data = _dataframe.copy()
    print(f'{time.ctime()} [{inspect.stack()[0].function}] modify')

    _original_data.loc[0] = ['USA', 'HOME', round(random(),2), round(random(),2)]

    cur_time = time.time()
    print(f'{time.ctime()} [{inspect.stack()[0].function}] startVaildation')
    _rflag = proceed_vaildation(_dataframe, _original_data, cntryLst)

    if not _rflag :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] ErrorVaildation')
        return

    print(f'{time.ctime()} [{inspect.stack()[0].function}] VaildationTime :{time.time()-cur_time:.2f} [sec]')

def proceed_vaildation(object, original, countries) :
    if object.shape != original.shape or (object.columns != original.columns).any() or (original.dtypes != object.dtypes).any():
        print(f'{time.ctime()} [{inspect.stack()[0].function}] Two Dataframes are not equal')
        return False

    VRF_RSDT = pd.DataFrame([], columns=['COUNTRY', 'AREA', 'CP', 'CP_ID'])

    for idx in range(len(countries)) :
        cnt_orgnl = original[original['COUNTRY'] == countries[idx]].values.tolist()
        cnt_trgt = object[object['COUNTRY'] == countries[idx]].values.tolist()

        if cnt_orgnl == cnt_trgt :
            VRF_RSDT = pd.concat([VRF_RSDT, pd.DataFrame(cnt_orgnl, columns=['COUNTRY', 'AREA', 'CP', 'CP_ID'])])
            VRF_RSDT['VAILD_RST'] = 'OK'
            VRF_RSDT = VRF_RSDT.reset_index(drop=True)
        
        else :
            # check if only difference data can be get.
            print(f'{time.ctime()} [{inspect.stack()[0].function}] match : {bool(cnt_orgnl == cnt_trgt)}')

            diff_dct = {}
            for idx in range(len(cnt_orgnl)) :
                _country = cnt_orgnl[idx][0]
                _area = cnt_orgnl[idx][1]
                _cp = cnt_orgnl[idx][2]
                _cpid = cnt_orgnl[idx][3]

                print(f'{time.ctime()} [{inspect.stack()[0].function}] country : {_country}, area : {_area}, cp : {_cp}, cpid : {_cpid}')

                if [_country, _area, _cp, _cpid] not in cnt_trgt :
                    diff_dct[_cp] = 'NOT DROPPED' 

            print(diff_dct)
            VRF_RSDT = pd.concat([VRF_RSDT, pd.DataFrame(cnt_orgnl, columns=['COUNTRY', 'AREA', 'CP', 'CP_ID'])])
            VRF_RSDT['VAILD_RST'] = VRF_RSDT['CP'].apply(lambda x : diff_dct.get(x, 'OK'))

        print(f'{time.ctime()} [{inspect.stack()[0].function}] \n{VRF_RSDT}')


    return True

if __name__ == '__main__' :
    # Verifylst = mock_ordering.proceedOrdering(PLATFORM_CODE) 
    data_vaildation(set_verification_data())


    