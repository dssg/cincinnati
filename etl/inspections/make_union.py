"""
Takes a list of date fields, makes a nice union statement. See events_timeline.sql for more information.
"""

tables = {"base": "inspections_raw.t_dssg_apd_base",
          "num0": "inspections_raw.t_dssg_APD_NUM0",
          "num1": "inspections_raw.t_dssg_APD_NUM1",
          "num2": "inspections_raw.t_dssg_APD_NUM2",}

fields = [("CBHCODE", "base", "date_a", "Reported"),
          ("CBHCODE", "base", "date_b", "Initial inspection"),
          ("CBHCODE", "base", "date_c", "Orders issued"),
          ("CBHCODE", "num1", "date_174", "Final notice"),
          ("CBHCODE", "base", "date_i", "Pre-prosecution status"),
          ("CBHCODE", "base", "date_h", "Civil 1"),
          ("CBHCODE", "num0", "date_072", "Civil 2"),
          ("CBHCODE", "num0", "date_026", "Prosecutor approves"),
          ("CBHBARRI", "base", "date_a", "Case created"),
          ("CBHBARRI", "base", "date_e", "Specification prepared"),
          ("CBHBARRI", "base", "date_i", "Barricade completed"),
          ("CBHBARRI", "base", "date_j", "Billed"),
          ("CBHBARRI", "base", "date_m", "Case closed"),
          ("LTTR-PR", "base", "date_b", "Initial inspection"),
          ("LTTR-PR", "base", "date_d", "Citation litter"),
          ("LTTR-PR", "base", "date_h", "Civil 1"),
          ("LTTR-PR", "base", "date_j", "Civil 2"),
          ("LTTR-PR", "base", "date_n", "Closed or transferred"),
          ("CBHHAZ_R", "base", "date_a", "Intake"),
          ("CBHHAZ_R", "num2", "date_221", "Nuisance hearing"),
          ("CBHHAZ_R", "base", "date_d", "Demolition")]



def make_select(process, table, column, name):
    return ("SELECT number_key, comp_type, {column} AS date, '{name}' AS event\n"
            "FROM {table}\n"
            "WHERE comp_type = '{process}'"
            " AND {column} IS NOT NULL\n").format(process=process,
                                                  table=tables[table],
                                                  column=column,
                                                  name=name)

selects = [make_select(proc, tab, col, nam)
           for proc, tab, col, nam in fields]
print ("UNION\n".join(selects))