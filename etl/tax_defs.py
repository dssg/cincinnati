abs_path = '/mnt/data/cincinnati/Taxes/taxinfo/'
file_2007 = abs_path + 'taxinfo2007.txt'
file_2008 = abs_path + 'taxinfo2008.txt'
file_2009 = abs_path + 'taxinfo2009.txt'
file_2010 = abs_path + 'taxinfo2010.txt'
file_2011 = abs_path + 'taxinfo2011.txt'
file_2012 = abs_path + 'taxinfo2012.txt'
file_2013 = abs_path + 'taxinfo2013.txt'
file_2014 = abs_path + 'taxinfo2014.txt'
file_2015 = abs_path + 'Tax_Information2015.CSV'

field_sizes_2007 = [20, 8, 25, 6, 3, 2, 1, 2, 3, 4, 3, 25, 25, 25, 25, 25,
                    25, 25, 25, 80, 80, 80, 80, 2, 1, 15, 1, 14, 10, 15, 1,
                   6, 8, 2, 15, 1, 15, 15, 1, 8, 2, 10, 1, 9, 10, 15, 15,
                   15, 15, 1, 1, 25, 25, 15, 10]
field_sizes_2008 = [20, 8, 25, 6, 3, 2, 1, 2, 3, 4, 3, 25, 25, 25, 25, 25,
                    25, 25, 25, 80, 80, 80, 80, 2, 1, 15, 1, 14, 10, 15, 1,
                   6, 8, 2, 15, 1, 15, 15, 1, 8, 2, 10, 1, 9, 10, 15, 15,
                   15, 15, 1, 1, 25, 25, 15, 10, 1]
field_sizes_2009 = [20, 8, 25, 6, 3, 2, 1, 2, 3, 4, 3, 25, 25, 25, 25, 25,
                    25, 25, 25, 80, 80, 80, 80, 2, 1, 15, 1, 14, 10, 15, 1,
                   6, 8, 2, 15, 1, 15, 15, 1, 8, 2, 10, 1, 9, 10, 15, 15,
                   15, 15, 1, 1, 25, 25, 15, 10, 1, 100]
field_sizes_2010_2014 = field_sizes_2009  # Tax data 2010-2014
# Fields from 2015 are comma separated

field_names_2007 = ['SMDA_NUM', 'UNIT', 'LOC_STREET', 'LOC_HOUSE_NO',
                    'LOC_SEC_NO', 'LOC_ST_DESC', 'LOC_ST_IND', 'LOC_ST_DIR',
                    'TAX_DIST', 'SCHOOL_CODE', 'CLASS_CODE', 'OWNER_LINE1',
                    'OWNER_LINE2', 'OWNER_LINE3', 'OWNER_LINE4',
                    'MAIL_LINE1', 'MAIL_LINE2', 'MAIL_LINE3', 'MAIL_LINE4',
                    'PROPERTY_DESCRIPTION1', 'PROPERTY_DESCRIPTION2',
                    'PROPERTY_DESCRIPTION3', 'PROPERTY_DESCRIPTION4',
                    'BOR_FLAG', 'VALID_SALE', 'MKT_LAND_VAL',
                    'HMSTD_FLAG', 'FILL_01', 'NUM_PARCELS', 'CAUV_VALUE',
                    'RED_25_FLAG', 'BANK_CODE', 'FILL_02', 'DEED_TYPE',
                    'MKT_IMPR_VAL', 'DIV_FLAG', 'SALE_AMOUNT', 'MKT_TOTAL_VAL',
                    'NEWS_CONS_FLAG', 'SALE_DATE', 'FORCL_FLAG', 'CONVEY_NO',
                    'SPEC_FLAG', 'FILL_03', 'DEED_NUMBER', 'ANNUAL_TAXES', 
                    'FRONT_FOOTAGE', 'ACRES', 'TAXES_PAID', 'FOX_DELETED',
                    'PAR_DELETED', 'PARCEL_ID', 'OWNER_SORT', 'DELQ_TAXES',
                    'ZIPCODE']
field_names_2008 = ['SMDA_NUM', 'UNIT', 'LOC_STREET', 'LOC_HOUSE_NO',
                    'LOC_SEC_NO', 'LOC_ST_DESC', 'LOC_ST_IND', 'LOC_ST_DIR',
                    'TAX_DIST', 'SCHOOL_CODE', 'CLASS_CODE', 'OWNER_LINE1',
                    'OWNER_LINE2', 'OWNER_LINE3', 'OWNER_LINE4',
                    'MAIL_LINE1', 'MAIL_LINE2', 'MAIL_LINE3', 'MAIL_LINE4',
                    'PROPERTY_DESCRIPTION1', 'PROPERTY_DESCRIPTION2',
                    'PROPERTY_DESCRIPTION3', 'PROPERTY_DESCRIPTION4',
                    'BOR_FLAG', 'VALID_SALE', 'MKT_LAND_VAL',
                    'HMSTD_FLAG', 'FILL_01', 'NUM_PARCELS', 'CAUV_VALUE',
                    'RED_25_FLAG', 'BANK_CODE', 'FILL_02', 'DEED_TYPE',
                    'MKT_IMPR_VAL', 'DIV_FLAG', 'SALE_AMOUNT', 'MKT_TOTAL_VAL',
                    'NEWS_CONS_FLAG', 'SALE_DATE', 'FORCL_FLAG', 'CONVEY_NO',
                    'SPEC_FLAG', 'FILL_03', 'DEED_NUMBER', 'ANNUAL_TAXES', 
                    'FRONT_FOOTAGE', 'ACRES', 'TAXES_PAID', 'FOX_DELETED',
                    'PAR_DELETED', 'PARCEL_ID', 'OWNER_SORT', 'DELQ_TAXES',
                    'ZIPCODE', 'RentalRegSw']
field_names_2009 = ['SMDA_NUM', 'UNIT', 'LOC_STREET', 'LOC_HOUSE_NO',
                    'LOC_SEC_NO', 'LOC_ST_DESC', 'LOC_ST_IND', 'LOC_ST_DIR',
                    'TAX_DIST', 'SCHOOL_CODE', 'CLASS_CODE', 'OWNER_LINE1',
                    'OWNER_LINE2', 'OWNER_LINE3', 'OWNER_LINE4',
                    'MAIL_LINE1', 'MAIL_LINE2', 'MAIL_LINE3', 'MAIL_LINE4',
                    'PROPERTY_DESCRIPTION1', 'PROPERTY_DESCRIPTION2',
                    'PROPERTY_DESCRIPTION3', 'PROPERTY_DESCRIPTION4',
                    'BOR_FLAG', 'VALID_SALE', 'MKT_LAND_VAL',
                    'HMSTD_FLAG', 'FILL_01', 'NUM_PARCELS', 'CAUV_VALUE',
                    'RED_25_FLAG', 'BANK_CODE', 'FILL_02', 'DEED_TYPE',
                    'MKT_IMPR_VAL', 'DIV_FLAG', 'SALE_AMOUNT', 'MKT_TOTAL_VAL',
                    'NEWS_CONS_FLAG', 'SALE_DATE', 'FORCL_FLAG', 'CONVEY_NO',
                    'SPEC_FLAG', 'FILL_03', 'DEED_NUMBER', 'ANNUAL_TAXES', 
                    'FRONT_FOOTAGE', 'ACRES', 'TAXES_PAID', 'FOX_DELETED',
                    'PAR_DELETED', 'PARCEL_ID', 'OWNER_SORT', 'DELQ_TAXES',
                    'ZIPCODE', 'RentalRegSw', 'Appraisal_Area']
field_names_2010_2014 = field_names_2009
field_names_2015 = ['PROPERTY_NUMBER', '2_AND_HALF_PERC_REDUCTION_FLAG',
                    'HMSTD_FLAG', 'BOOK', 'PAGE', 'PARCEL', 'MLTOWN',
                    'CLASS_CODE', 'CLASS_CODE_DESC',
                    'AUD_APPRAISAL_CODE', 'AUD_APPRAISAL_CODE_DESC',
                    'OWNER_NAME', 'OWNER_ATTN', 'OWNER_ST_NO', 'OWNER_ST_DIR',
                    'OWNER_ST_NAME', 'OWNER_ST_SUFFIX',
                    'OWNER_ST_SUFFIX_DIR', 'OWNER_SECONDARY_ADDR',
                    'OWNER_CITY', 'OWNER_STATE', 'OWNER_ZIP', 'OWNER_COUNTRY',
                    'LOC_HOUSE_NO', 'LOC_ST_DIR', 'LOC_ST_DIR', 'LOC_ST_NAME',
                    'LOC_ST_SUFFIX', 'LOC_CITY', 'LOC_STATE', 'LOC_ZIP',
                    'MAIL_NAME', 'MAIL_ATTN', 'MAIL_ST_NO', 'MAIL_ST_DIR',
                    'MAIL_ST_NAME', 'MAIL_ST_SUFFIX', 'MAIL_ST_SUFFIX_DIR',
                    'MAIL_SECONDARY_ADDR', 'MAIL_CITY', 'MAIL_STATE', 'MAIL_ZIP',
                    'MAIL_COUNTRY', 'PROPERTY_DESCRIPTION1', 'PARCEL_DIVIDED_FLAG',
                    'NEW_CONSTRUCTION_FLAG', 'SPECIAL_FLAG', 'SCHOOL_CODE',
                    'SCHOOL_CODE_DESC', 'TAX_DISTRICT', 'TAX_DISTRICT_DESC',
                    'FORCL_FLAG', 'ACRES', 'FRONT_FOOTAGE', 'RENTAL_REG',
                    'BOR_FLAG', 'SALE_DATE', 'SALE_AMOUNT', 'NUM_PARCELS',
                    'CONVEY_NO', 'DEED_NUMBER', 'SALE_SOURCE', 'SALE_TYPE',
                    'PREV_OWNER_NAME', 'PREV_OWNER_ATTN_LINE', 'AGRI_USE_VALUE',
                    'MKT_LAND_VAL', 'MKT_IMPR_VAL', 'MKT_TOTAL_VAL', 
                    'TOTAL_LAND_VALUE', 'ANNUAL_TAXES', 'TAXES_PAID', 'DELQ_TAXES',
                    'DELQ_TAXES_PAID', 'PARCEL_ACTIVE_CURR_YR_FLAG']
