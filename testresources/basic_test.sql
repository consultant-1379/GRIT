-- create tables with test data
-- value is the value to test
-- tst is the test to use
-- tst 0 - both sides the same
-- tst 1 - left has value not in right
-- tst 2 - right has value not in left
-- tst 3 - left has duplicated value
-- tst 4 - right has duplicated value
-- tst 5 - left and right have some same and some different values
-- tst 6 - No matching data 
-- tst 7 - count of instances in tst 1 
-- tst 8 - sum of instances in tst 1 with values > 1 

drop table if exists basic_table1;
create table basic_table1 (
    val as int null,
    tst as int null,
    ipv4 as binary(4) null
);

drop table if exists basic_table2;
create table basic_table2 (
    val as int null,
    tst as int null,
    ipv4 as binary(4) null
);

insert into basic_table1 (val, tst) values
 (1,0),
 (2,0),
 (3,0),
 (4,1),
 (6,3),
 (6,3),
 (7,4),
 (8,5),
 (9,5),
 (10,5);
 
insert into basic_table2 (val, tst) values
 (1,0),
 (2,0),
 (3,0),
 (5,2),
 (6,3),
 (7,4),
 (7,4),
 (8,5),
 (11,5),
 (11,5),
 (3,7),
 (2,8); 

insert into basic_table1 (val, tst, ipv4) values
 (0,98,0x01020304),
 (0,99,0x01020304),
 (0,99,0xffeeddcc);

insert into basic_table2 (val, tst, ipv4) values
 (0,98,0x01020301),
 (0,99,0x01020304),
 (0,99,0xffeeddcc);

