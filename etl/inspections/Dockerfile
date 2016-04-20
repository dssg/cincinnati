FROM wnameless/oracle-xe-11g
MAINTAINER Eduardo Blancas Reyes

#Install some dependencies
RUN apt-get update
RUN apt-get install -y make
RUN apt-get install -y gcc

#Download and install ora2pg
RUN wget -O ora2pg-17.3.tar.gz https://github.com/darold/ora2pg/archive/v17.3.tar.gz
RUN tar xzf ora2pg-17.3.tar.gz
WORKDIR ora2pg-17.3/
RUN perl Makefile.PL
RUN make && make install

#Install DBD::Oracle
ENV LD_LIBRARY_PATH=$ORACLE_HOME/lib
RUN perl -MCPAN -e 'install DBD::Oracle'

#Copy conf file
COPY ora2pg.conf /etc/ora2pg/
