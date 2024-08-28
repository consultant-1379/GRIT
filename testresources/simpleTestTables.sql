--Create Tables
    drop table if exists table1;
    create table table1 (
    id as int null,
    col2 as varchar(32) null,
	col3 as int null);

    insert into table1 (id, col2, col3) values (1, 'rnc01', 1);
    insert into table1 (id, col2, col3) values (1, 'rnc02', null);
    insert into table1 (id, col2, col3) values (1, 'rnc03', 3);
    insert into table1 (id, col2, col3) values (1, 'rnc04', 5);
    insert into table1 (id, col2, col3) values (2, 'rnc01', 1);
    insert into table1 (id, col2, col3) values (2, 'rnc02', null);
    insert into table1 (id, col2, col3) values (2, 'rnc03', null);

    drop table if exists table2;
    create table table2 (
    event_id as int null,
    col2 as varchar(32) null,
	col3 as int null);    
    
    insert into table2 (event_id, col2, col3) values (1, 'rnc01', 1);
    insert into table2 (event_id, col2, col3) values (1, 'rnc02', 0);
    insert into table2 (event_id, col2, col3) values (1, 'rnc03', 3);
    insert into table2 (event_id, col2, col3) values (1, 'rnc04', 5);
    insert into table2 (event_id, col2, col3) values (2, 'rnc01', 1);
    insert into table2 (event_id, col2, col3) values (2, 'rnc02', 0);
    insert into table2 (event_id, col2, col3) values (2, 'rnc04', 0);
   
    drop table if exists tableDHM;
    create table tableDHM (
    datefld as int,
    hourfld as int,
    minfld  as int, 
    event_id as int null,
    col2 as varchar(32) null,
	col3 as int null);    
    
    insert into tableDHM (dateFld, hourfld, minfld, event_id, col2, col3) values
       ( 1, 2, 3, 1, 'rnc01', 1),
       ( 1, 2, 4, 1, 'rnc01', 1),
       ( 1, 3, 4, 1, 'rnc01', 1),
       ( 1, 4, 4, 1, 'rnc01', 1),
       ( 1, 5, 4, 1, 'rnc01', 1),
       ( 2, 1, 4, 1, 'rnc01', 1),
       ( 2, 2, 4, 1, 'rnc01', 1),
       ( 2, 3, 5, 1, 'rnc01', 1),
       ( 2, 4, 5, 1, 'rnc01', 1),
       ( 3, 2, 4, 1, 'rnc01', 1),
       ( 3, 3, 5, 1, 'rnc01', 1);
       
    drop table if exists tableDHM1;
    create table tableDHM1 (
    datefld as date,
    hourfld as int,
    minfld  as int, 
    event_id as int null,
    col2 as varchar(32) null,
	col3 as int null);    
    
    insert into tableDHM1 (dateFld, hourfld, minfld, event_id, col2, col3) values
       ( '2015-04-21', 2, 3, 1, 'rnc01', 1),
       ( '2015-04-22', 2, 4, 1, 'rnc01', 1),
       ( '2015-04-22', 3, 4, 1, 'rnc01', 1),
       ( '2015-04-22', 4, 4, 1, 'rnc01', 1),
       ( '2015-04-22', 5, 4, 1, 'rnc01', 1),
       ( '2015-04-23', 1, 4, 1, 'rnc01', 1),
       ( '2015-04-23', 2, 4, 1, 'rnc01', 1),
       ( '2015-04-23', 3, 5, 1, 'rnc01', 1),
       ( '2015-04-23', 4, 5, 1, 'rnc01', 1),
       ( '2015-04-24 12:34:56', 2, 4, 1, 'rnc01', 1),
       ( '2015-04-24 23:45:01', 3, 5, 1, 'rnc01', 1);
   
    drop table if exists tableDHM2;
    create table tableDHM2 (
    datefld as date,
    hourfld as int,
    minfld  as int, 
    event_id as int null,
    col2 as varchar(32) null,
	col3 as int null);    
    
    insert into tableDHM2 (dateFld, hourfld, minfld, event_id, col2, col3) values
       ( '2015-04-22', 1, 4, 1, 'rnc01', 1),
       ( '2015-04-22', 2, 4, 1, 'rnc01', 1),
       ( '2015-04-23', 3, 5, 1, 'rnc01', 1),
       ( '2015-04-24', 4, 5, 1, 'rnc01', 1);
   
commit;