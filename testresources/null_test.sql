drop table if exists null_input_test;
create table null_input_test (
col1 as int null);
drop table if exists null_output_test;
create table null_output_test(
col1 as int null);
insert into null_input_test (col1) values
(null),
(null),
(null),
(null),
(null),
(8),
(9);

insert into null_output_test (col1) values
(null),
(null),
(null),
(null),
(null),
(8),
(9);

commit;