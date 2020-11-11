-- comp9311 19T3 Project 1
--
-- MyMyUNSW Solutions

--student name:Luyang Ye
--student id:z5280537

-- Q1:
create or replace view Q1(courseid, code)
as
select distinct c.id as courseid, s.code as code
from courses c, subjects s, Course_staff cs, Staff_roles sr
where c.subject = s.id AND code like 'LAWS%' AND c.id = cs.course AND cs .role = sr.id AND sr.name = 'Course Tutor'
--... SQL statements, possibly using other views/functions defined by you ...
--... DISTINCT course id and cubject code of any cours that is taught by course tutor(LAWS only)
;

-- Q2:
create or replace view Q2(unswid,name,class_num)
as
select distinct b.unswid as unswid, b.name as name, count(*) as class_num
from Buildings b, Class_types ct, rooms r, classes c
where ct.id = c.ctype and c.room = r.id and r.building = b.id and ct.name = 'Lecture'
group by b.unswid, b.name
--... SQL statements, possibly using other views/functions defined by you ...
--... DISTINCT building id, name and # of lecture class(class_type.name) taken in building(at least one)
;

-- Q3:
create or replace view Q3(classid, course, room)
as 
select distinct c.id as classid, c.course as course, c.room as room
from Classes c, Rooms r, facilities f, room_facilities rf, people p, course_enrolments ce
where c.room = r.id AND r.id = rf.room AND rf.facility = f.id AND f.description = 'Television monitor' AND p.id = ce.student AND ce.course = c.course AND p.name = 'Craig Conlon'
--... SQL statements, possibly using other views/functions defined by you ...
--... distinct classes equipped with Television monitor, enrolled by student 'Craig Conlon'
;

-- Q4:
create or replace view Q4(unswid, name)
as
select distinct p.unswid as unswid, p.name as name
from People p, Course_enrolments ce, students s, subjects sb, courses c
where p.id = s.id AND p.id = ce.student AND c.subject = sb.id AND c.id = ce.course AND s.stype = 'local' AND ce.grade = 'CR' AND sb.code = 'COMP9311' 
INTERSECT
select distinct p.unswid as unswid, p.name as name
from People p, Course_enrolments ce, students s, subjects sb, courses c
where p.id = s.id AND p.id = ce.student AND c.subject = sb.id AND c.id = ce.course AND s.stype = 'local' AND ce.grade = 'CR' AND sb.code = 'COMP9021' 
--... SQL statements, possibly using other views/functions defined by you ...
;

--Q5:
create or replace view Q5(num_student)
as
select count(*)
from
(select distinct s.id as sid, avg(ce.mark) as av from Students s, Course_enrolments ce where s.id = ce.student group by s.id Having count(mark IS NOT NULL) >= 1) as temp
where temp.av > 
(select avg(temp1.av) from (select distinct s.id as sid, avg(ce.mark) as av from Students s, Course_enrolments ce where s.id = ce.student group by s.id Having count(mark IS NOT NULL) >= 1) as temp1)
--... SQL statements, possibly using other views/functions defined by you ...
;

-- Q6:
--...count number of students enrol in each course group by c.id, c.semester
create or replace view Q6_1(courseid, semester, num)
as
select c.id as courseid, c.semester as semester, count(*) as num
from Courses c, Course_enrolments ce
where c.id = ce.course
group by c.id, c.semester
having count(*) >= 10;

--...find max_num_student for each semester
create or replace view Q6_2(semester, max_num)
as
select Q6_1.semester as semester, max(Q6_1.num) as max_num
from Q6_1
group by Q6_1.semester;

--...find semesters with minimum max_num_student
create or replace view Q6(semester, max_num_student)
as
select s.longname as semester, Q6_2.max_num as max_num_student
from Semesters s, Q6_2
where s.id = Q6_2.semester AND Q6_2.max_num = (select min(Q6_2.max_num) from Q6_2)
--... SQL statements, possibly using other views/functions defined by you ...
;

-- Q7:
create or replace view Q7_1(course, avgmark, semester)
as
select c.id as course, cast(avg(ce.mark) as numeric(4,2)) as avgmark, s.name as semester
from Courses c, Course_enrolments ce, Semesters s
where c.id = ce.course and c.semester = s.id and (s.year = 2009 or s.year = 2010)
group by c.id, s.name
having count(ce.mark IS NOT NULL) > 20;

create or replace view Q7(course, avgmark, semester)
as
select q.course as course, q.avgmark as avgmark, q.semester as semester
from Q7_1 q
where q.avgmark > 80;
--... SQL statements, possibly using other views/functions defined by you ...
;

-- Q8: 
--all stream enrolments
create or replace view s1
as
select p.unswid, t.year, t.term, st.name, sn.stype
from People p, Program_enrolments pe, Stream_enrolments se, Streams st, Semesters t, Students sn
where p.id=pe.student and pe.id=se.partof and se.stream=st.id and t.id=pe.semester and p.id=sn.id
;

--all course enrolments
create or replace view s2
as
select p.unswid, c.id as course, s.id as sub, u.name as unit, sn.stype
from People p, Students sn, course_enrolments ce, courses c, subjects s, OrgUnits u
where p.id=sn.id and ce.student = sn.id and ce.course = c.id and c.subject = s.id and s.offeredby=u.id
;

--local student enrol law stream in 2008
create or replace view s3
as
select distinct unswid
from s1
where name = 'Law' and year=2008 and stype='local'
;
--never enrol in course offered by Accounting or Economics
create or replace view s4
as
select unswid
from s2
where unswid not in(select unswid from s2 where unit = 'Accounting') and stype='local'
;
create or replace view s5
as
select unswid
from s2
where unswid not in(select unswid from s2 where unit = 'Economics') and stype='local'
;
--local student enrol law stream in 2008 and never enrol in course offered by Accounting
Create or replace view s6
as
select unswid from s3
INTERSECT
select unswid from s4
;
--local student enrol law stream in 2008 and never enrol in course offered by Accounting or Economics
Create or replace view s7
as
select unswid from s6
INTERSECT
select unswid from s5
;
--q8 final answer
create or replace view Q8(num)
as
select count(distinct unswid) as num
from s7
;

-- Q9:
-- 2003 to 2012 major semesters
create or replace view t1(sem_id, year, term)
as
select id, year, term
from Semesters s
where year BETWEEN 2003 and 2012
and
(term = 'S1' or term = 'S2');
--level 9 COMP subjects in major semesters;
create or replace view t2(code, name, id)
as
select code, name, id
from Subjects
where code like 'COMP9%'
and
id IN(
	select subject
	from Courses
	where semester IN(
		select sem_id
		from t1
	)
	group by subject
	HAVING COUNT(semester) >= 20
);
--all students
create or replace view t3
as
select p.unswid, p.name, c.id as course, s.id as sub, ce.grade as grade
from People p, Students sn, course_enrolments ce, courses c, subjects s
where p.id=sn.id and ce.student = sn.id and ce.course = c.id and c.subject = s.id
;
--students enroll in popular level 9 COMP subjects
create or replace view t4
as
select t3.unswid, t3.name, t3.grade
from t2, t3
where t3.sub = t2.id;
--students enroll in popular level 9 COMP subjects get good performance
create or replace view t5
as
select * from t4 where grade = 'HD' or grade = 'DN';
--students get good per formance in all popular level 9 COMP subject
create or replace view t6
as
select t5.unswid, t5.name from t5 group by t5.unswid, t5.name HAVING count(t5.grade) >= (select count(*) from t2);
--q9 final answer
create or replace view Q9(unswid, name)
as
select unswid as unswid, name as name from t6;
--... SQL statements, possibly using other views/functions defined by you ...
;

-- Q10:
--all Lecture Theatre
create or replace view n1
as
select r.id, r.unswid, r.longname 
from rooms r, room_types rt
where r.rtype = rt.id and rt.description = 'Lecture Theatre';

--all classes 2010 s2
create or replace view n2
as
select classes.id, classes.room
from classes, courses, semesters
where classes.course = courses.id and courses.semester = semesters.id and semesters.year = 2010 and semesters.term = 'S2';
--select c.id, c.room, s.year, s.term
--from classes c, semesters s, course_enrolments ce, courses co
--where ce.course = co.id and c.course = co.id and co.semester = s.id and s.year = 2010 and s.term = 'S2';

--all Lecture Theatre with classes in 2010 s2
create or replace view n3
as
select n1.unswid, n1.longname, count(distinct n2.id) as num
from n1 left join n2 on n1.id = n2.room
group by n1.unswid, n1.longname;
--final answer of q10
create or replace view Q10(unswid, longname, num, rank)
as
select *, rank() over(order by num desc) rank from n3;
--... SQL statements, possibly using other views/functions defined by you ...
;

-- Q11:
--all students with all programs
create or replace view a1
as
select distinct p.unswid, p.name, sm.year, sm.term, pd.abbrev, pr.id as pid, pr.uoc, ce.mark, su.uoc as suoc, co.id as cid
from people p, programs pr, program_enrolments pe, program_degrees pd, semesters sm, course_enrolments ce, courses co, subjects su
where pe.student = p.id and pe.semester = sm.id and pe.program = pr.id and pd.program = pr.id and ce.student = p.id and ce.course = co.id and co.subject = su.id and co.semester = sm.id
;

--all students enroll in program BSc
create or replace view a2
as
select * from a1 where abbrev = 'BSc'
;
--students pass at least one BSc course in 2010 s2
create or replace view a3
as
select *
from a2
where unswid in(select unswid from a2 where year = 2010 and term = 'S2' and mark >= 50)
;
--all BSc courses the students has passed beofore 2011
create or replace view a4
as
select distinct *
from a3
where year < 2011 and mark >= 50
;

--averge mark of all courses the student has passed before 2011 >= 80
create or replace view a5
as
select unswid, name, pid, uoc, mark, suoc, cid
from a4
where unswid in(select unswid from a4 group by unswid having avg(mark) >= 80)
;

--total uoc earned before 2011(exclusive) no less than required uoc
create or replace view a6
as
select distinct unswid, name, pid, sum(suoc)
from a5
group by unswid, name, uoc, pid
having sum(suoc) >= uoc
;
--final answer of Q11
create or replace view Q11(unswid, name)
as
select unswid, name
from a6
--... SQL statements, possibly using other views/functions defined by you ...
;

-- Q12:
--all students with all programs
create or replace view k1
as
select distinct p.unswid, p.name, sm.id as sid, pd.abbrev, pr.name as pname, ce.mark, su.uoc, co.id as cid
from people p, programs pr, program_enrolments pe, program_degrees pd, semesters sm, course_enrolments ce, courses co, subjects su
where pe.student = p.id and pe.semester = sm.id and pe.program = pr.id and pd.program = pr.id and ce.student = p.id and ce.course = co.id and co.subject = su.id and co.semester = sm.id
;
--all students enroll in program MSc
create or replace view k2
as
select * from k1 where abbrev = 'MSc';
--all MSc students whose unswid start with 329
create or replace view k3
as
select distinct *
from k2
where unswid between 3290000 and 3299999
;
--for each students, only consider course_enrolments.mark>=0;
create or replace view k4
as
select * 
from k3
where k3.mark >=0
;
--calculate total UOC failed
create or replace view k5
as
select unswid, name, pname, sum(uoc) as totalF
from k4
where mark < 50
group by unswid, name, pname
;
create or replace view k6
as 
select distinct unswid, name, pname, 0 as totalF
from k4
where unswid not in(select unswid from k5)
;
create or replace view k7
as
select * from k5
UNION
select * from k6
;

--final answer of q12
create or replace view Q12(unswid, name, program, academic_standing)
as
select unswid, name, pname as program, 
  case when totalF < 12 then 'Good' when totalF between 12 and 18 then 'Probation' else 'Exclusion' end as academic_standing
from k7
--... SQL statements, possibly using other views/functions defined by you ...
;
