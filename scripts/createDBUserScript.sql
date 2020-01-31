drop user medrec cascade;
create user medrec identified by medrec;
grant create session to medrec;
grant create table,create view to medrec; 
grant  create procedure to medrec;
grant create synonym, create trigger to medrec;
grant unlimited tablespace to medrec;