d = DATA['FULL_PROJECT_NUM'].drop_duplicates(['FULL_PROJECT_NUM'])
d = DATA['CFDA_CODE'].drop_duplicates(['CFDA_CODE'])


for project in d:
  tmp = DATA[DATA.FULL_PROJECT_NUM == project]
  if len(tmp)>1:
    print tmp

d2 = DATA[['ACTIVITY', 'SUPPORT_YEAR']].drop_duplicates(['ACTIVITY', 'SUPPORT_YEAR'])

d3 = DATA[['FUNDING_IC', 'FUNDING_MECHANISM']].drop_duplicates(['ACTIVITY', 'FUNDING_MECHANISM'])

d3 = DATA[['ADMINISTERING_IC', 'FUNDING_ICs']].drop_duplicates(['ADMINISTERING_IC', 'FUNDING_ICs'])

d3 = DATA[['FULL_PROJECT_NUM', 'SERIAL_NUMBER', 'CORE_PROJECT_NUM']].drop_duplicates(['FULL_PROJECT_NUM', 'SERIAL_NUMBER', 'CORE_PROJECT_NUM'])
