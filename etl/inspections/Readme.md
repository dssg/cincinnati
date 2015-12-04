# Introduction

We describe here how we imported the PermPlus oracle database and the auditor_building_info dataset  into posgres. 
We have also generated some views on this data, this process is described at the end of this file. 

# Import auditor_building_info

1. Log into a server that has oracle running.

2. Make a directory /home/oracle/cincinnati and place Oracle dmp file there, get in there

3. Become the oracle user

     su -u oracle

4. Learn which tables are in the dmp file (see the created logfile)

    imp SYSTEM/<PASSWD> file=auditor_building_info.dmp SHOW=Y log=auditor_building_info.info FULL=Y

5. Make a new user (=new schema) for each dmp file to keep tables separate from each other

    create user cincinnati_auditors identified by password default tablespace users;
    grant connect to cincinnati_auditors;
    grant create table to cincinnati_auditors;
    grant unlimited tablespace to cincinnati_auditors;

6. Perform the import. A new table cincinnati_auditors.BLD_INFO will be created.

    imp SYSTEM/<PASSWD> file=auditor_building_info.dmp fromuser=CAGDBA touser=cincinnati_auditors

7. Export CREATE TABLEs to postgres dump, needs config and tool from Kenny

    ora2pg -c ../oracle_export/export.conf -t TABLE -n cincinnati_auditors -o /mnt/oracle_data/cincinnati/auditor_building_info.tables.sql

8. Export the actual data

    nohup ora2pg -c ../oracle_export/export.conf -t COPY -n cincinnati_auditors -o /mnt/oracle_data/cincinnati/auditor_building_info.data.sql

9. Load into postgres

    psql -h $DB_HOST -U $DB_USER -d $DB_NAME < auditor_building_info.tables.sql

    psql -h $DB_HOST -U $DB_USER -d $DB_NAME < auditor_building_info.data.sql


# Import raw PermPlus database into postgres

    imp SYSTEM/<PASSWD> file=raw_vendor_tables.dmp fromuser=DBADLS touser=cincinnati_violations

    ora2pg -c ../oracle_export/export.conf -t TABLE -n cincinnati_violations -o /mnt/oracle_data/cincinnati/raw_vendor_tables.tables.sql

    nohup ora2pg -c ../oracle_export/export.conf -t COPY -n cincinnati_violations -o /mnt/oracle_data/cincinnati/raw_vendor_tables.data.sql

# Import violations / inspections export into postgres

    imp SYSTEM/<PASSWD> file=cag_code_violations.dmp fromuser=DBADLS touser=cincinnati_violations2 

    ora2pg -c ../oracle_export/export.conf -t TABLE -n cincinnati_violations2 -o /mnt/oracle_data/cincinnati/cag_code_violations.tables.sql

    nohup ora2pg -c ../oracle_export/export.conf -t COPY -n cincinnati_violations2 -o /mnt/oracle_data/cincinnati/cag_code_violations.data.sql
    
    
# Make violations view

We have built (and excessively use) a timeline view of the raw data. This view lists inspection events (e.g. complaint 
made, initial inspection, (violation) order issued, fined) for all parcels, together with the information on when this 
event occurred. To make this view, executed the `events_timeline.sql` script.