# hostname: localhost
# port: 49161
# sid: xe
# username: system
# password: oracle


#https://github.com/dssg/cincinnati2015-public/tree/master/etl/inspections 


#Pull Docker image
docker pull wnameless/oracle-xe-11g

#Run container
docker run -d -p 49160:22 -p 49161:1521 -v $DATA_FOLDER/etl/inspections:/root/data wnameless/oracle-xe-11g

#SSH
ssh root@localhost -p 49160
#password: admin


apt-get update
apt-get install make
apt-get install gcc

#Download and install ora2pg
wget -O ora2pg-17.3.tar.gz https://github.com/darold/ora2pg/archive/v17.3.tar.gz
tar xzf ora2pg-17.3.tar.gz
cd ora2pg-17.3/
perl Makefile.PL
make && make install


#Install DBD::Oracle
export LD_LIBRARY_PATH=$ORACLE_HOME/lib
#perl -MCPAN -e 'install DBI'
perl -MCPAN -e 'install DBD::Oracle'
#yes



#List tables in the dmp file (see the created logfile)
#imp SYSTEM/ file=inspections.dmp SHOW=Y log=inspections.info FULL=Y

#sqlplus
#create user cinci identified by password default tablespace users;
#grant connect to cinci;
#grant create table to cinci;
#grant unlimited tablespace to cinci;

imp SYSTEM/oracle file=/root/data/inspections.dmp fromuser=DBADLS touser=cinci

ora2pg -c /root/data/ora2pg.conf -t TABLE -n cinci -o /root/data/testing.tables.sql

#ora2pg -c ../oracle_export/export.conf -t TABLE -n cincinnati_violations -o /mnt/oracle_data/cincinnati/raw_vendor_tables.tables.sql

# nohup ora2pg -c ../oracle_export/export.conf -t COPY -n cincinnati_violations -o /mnt/oracle_data/cincinnati/raw_vendor_tables.data.sql


#Shut down container
#docker kill drunk_kilby
