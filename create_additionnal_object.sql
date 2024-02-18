create view FILE_extention as
select f.extention , count(1)
from FILE f 
group by f.extention
order by 2 desc ;


create view FILE_author as
select f.all_author , count(1)
from FILE f 
group by f.all_author
order by 2 desc ;


create view FILE_year as
select f.all_author , count(1)
from FILE f 
group by f.year
order by 2 desc



create view FILE_sha256 as
    select f.sha256
	from FILE f 
	group by f.sha256
	having count(f.sha256) > 1 ;


DROP TABLE IF EXISTS FILE_duplicate ;

create table FILE_duplicate as
select f.sha256, group_concat(f.file), group_concat(f.extention), f.size/1000000, count(1), sum(f.size)/1000000
from FILE f, FILE_sha256 sha
where f.sha256 = sha.sha256 
group by f.sha256, f.size









erwan@airnas (22:06) ~ $ df
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       2.3G  1.2G  1.1G  54% /
devtmpfs        244M     0  244M   0% /dev
/dev/sda3       3.6T  3.3T  380G  90% /volume1
erwan@airnas (22:06) ~ $ \df
Filesystem      1K-blocks       Used Available Use% Mounted on
/dev/sda1         2385592    1215444   1051364  54% /
devtmpfs           248848          0    248848   0% /dev
tmpfs              250824         24    250800   1% /dev/shm
tmpfs              250824      20844    229980   9% /run
tmpfs              250824          0    250824   0% /sys/fs/cgroup
tmpfs              250824        640    250184   1% /tmp
/dev/sda3      3840911984 3442972688 397820512  90% /volume1
erwan@airnas (22:06) ~ $



