-- Test data for lookup tests
drop table if exists file_lk_raw_1;
create table file_lk_raw_1 (
date_id date,
hour_id int null, 
min_id int null, 
gummei varchar(14) null,
rnc_id as int,
gcellid int);


-- gcellid
-- cellid = gcellid % 256 => gcellid - gcellid / 256 * 256
-- nodeid = gcellit / 256
-- 12345 - cellid = 57, nodeid = 48
-- 12346 - cellid = 58, nodeid = 48
insert into file_lk_raw_1 (date_id, hour_id, min_id, gummei, rnc_id, gcellid) values 
('2015-04-16', 20, 20, '0013f410000401', 1, 12345),
('2015-04-16', 20, 20, '0013f410000401', 2, 12346),
('2015-04-16', 20, 20, '0013f410000401', 3, 12347),
('2015-04-16', 20, 20, '0013f410000401', 4, 12348),
('2015-04-16', 20, 20, '0013f410000401', 4, 12349),
('2015-04-16', 20, 20, '0013f410000401', 4, 12350);


drop table if exists eniq_lk_test_raw;
create table eniq_lk_test_raw (
date_id date, 
hour_id int null, 
min_id int null, 
mcc varchar(3) null, 
mnc varchar(3),
mncint int, 
rnc_name varchar(32),
nodeid int,
cellid int );


insert into eniq_lk_test_raw (date_id, hour_id, min_id, mcc, mnc, mncint, nodeid, cellid, rnc_name) values
('2015-04-16', 20, 20, '310', '410', 410, 48, 57, 'rnc01', ),
('2015-04-16', 20, 20, '310', '410', 410, 48, 58, 'rnc02'),
('2015-04-16', 20, 20, '310', '410', 410, 48, 59, 'rnc03'),
('2015-04-16', 20, 20, '310', '410', 410, 48, 60, 'rnc04'),
('2015-04-16', 20, 20, '310', '410', 410, 48, 61, 'rnc04'),
('2015-04-16', 20, 20, '310', '410', 410, 48, 62, 'rnc04');

drop table if exists dim_e_lk_rnc_test;
create table dim_e_lk_rnc_test(
	rnc_id int,
	rnc_name varchar(32));
insert into dim_e_lk_rnc_test (rnc_id, rnc_name) values 
	(1, 'rnc01'),
	(2, 'rnc02'),
	(2, 'rnc02'),  -- duplicate entry needs to be handled by lookup
	(3, 'rnc03'),
	(4, 'rnc04');
	
drop table if exists dim_e_mccmnc_test;
create table dim_e_mccmnc_test(
   mcc varchar(3),
   mnc varchar(3),
   country varchar(10));  

insert into dim_e_mccmnc_test (mcc, mnc, country) values 
	('310','410', 'Ireland'),
	('310','411', 'Eire'),
	('310','412', 'RoI'),
	('309','41', ''),
	('309','42', ''),
	('309','43', '');

drop table if exists dim_e_mccmnc_test2;
create table dim_e_mccmnc_test2(
   mcc varchar(3),
   mnc varchar(3),
   country varchar(10));  

insert into dim_e_mccmnc_test2 (mcc, mnc, country) values 
	('310','410', 'Ireland'),
	('310','411', 'Eire'),
	('310','412', 'RoI'),
	('309','41', ''),
	('309','42', ''),
	('309','43', '');



commit;
