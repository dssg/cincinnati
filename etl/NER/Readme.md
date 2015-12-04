### Resolve whether properties are owned by people or organizations

Download Stanford Name Entity Recognition from http://nlp.stanford.edu/software/CRF-NER.shtml

Unpack downloaded archive, then start NER server using

    java -mx6000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -port 9191 -loadClassifier \
    classifiers/english.all.3class.distsim.crf.ser.gz -tokenizerFactory edu.stanford.nlp.process.WhitespaceTokenizer \
    -tokenizerOptions "tokenizeNLs=true" -outputFormat tsv  &
    
Perform NER for all tax data from 2007 to 2015. One CSV is written per year. Must use python3 for this step!

    python get_tax_owners.py

Combine all those CSVs into one CSV

    python merge.py
    
Create new table in the database 

    CREATE TABLE public.taxes_owners (
	 parcel_id VARCHAR(12) PRIMARY KEY, 
	 owner_2007 VARCHAR(12), 
	 owner_2008 VARCHAR(12),
	 owner_2009 VARCHAR(12),
	 owner_2010 VARCHAR(12),
	 owner_2011 VARCHAR(12),
	 owner_2012 VARCHAR(12),
	 owner_2013 VARCHAR(12),
	 owner_2014 VARCHAR(12),
	 owner_2015 VARCHAR(12));
	 
Upload the data to the database

    cat owners_2007-2015.csv | psql -h $DB_HOST -U $DB_USER \
    -d $DB_NAME -c "\COPY public.taxes_owners FROM STDIN  WITH CSV HEADER DELIMITER ',';"
