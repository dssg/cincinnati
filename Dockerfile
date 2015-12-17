FROM ubuntu:trusty

#Install common packages
RUN apt-get install -y software-properties-common

#Add repository with the required GDAL version
RUN add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable && apt-get update
RUN apt-get install -y gdal-bin
RUN gdalinfo --version

#Install mdbtools to convert access databases to csv files
RUN apt-get install -y mdbtools

#Install required java version for NER (Java 1.8 or later)
#http://www.webupd8.org/2012/09/install-oracle-java-8-in-ubuntu-via-ppa.html
RUN add-apt-repository -y ppa:webupd8team/java && apt-get update
#Auto accept Oracle license
RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections
#RUN apt-get update
RUN apt-get install -y oracle-java8-installer

#Setup enviromental variables
ENV ROOT_FOLDER=/root/code
ENV DATA_FOLDER=/root/data

#Set /root as working dir
WORKDIR /root