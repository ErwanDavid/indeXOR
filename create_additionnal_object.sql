DROP view IF EXISTS FILE_type ;

create view FILE_type as
select f.typedesc , count(1), sum(f.size)
from FILE f 
group by f.typedesc
order by 3 desc ;


DROP view IF EXISTS FILE_author ;

create view FILE_author as
select f.all_author , count(1)
from FILE f 
group by f.all_author
order by 2 desc ;


DROP view IF EXISTS FILE_year ;

create view FILE_year as
select f.all_author , count(1)
from FILE f 
group by f.year
order by 2 desc

DROP view IF EXISTS FILE_sha256 ;

create view FILE_sha256 as
    select f.sha256
	from FILE f 
	group by f.sha256
	having count(f.sha256) > 1 ;


DROP TABLE IF EXISTS FILE_duplicate ;
create view FILE_type as
select f.typedesc , count(1), sum(f.size)
from FILE f 
group by f.typedesc
order by 3 desc ;
create table FILE_duplicate as
select f.sha256, group_concat(f.file), group_concat(f.extention), f.size/1000000, count(1), sum(f.size)/1000000
from FILE f, FILE_sha256 sha
where f.sha256 = sha.sha256 
group by f.sha256, f.size

