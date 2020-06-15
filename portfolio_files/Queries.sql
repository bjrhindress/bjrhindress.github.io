SET PAGESIZE 75
SET LINESIZE 165

COLUMN "1" FORMAT 9999999
COLUMN "2" FORMAT 9999999
COLUMN "3" FORMAT 9999999
COLUMN "4" FORMAT 9999999
COLUMN "5" FORMAT 9999999
COLUMN "6" FORMAT 9999999
COLUMN "7" FORMAT 9999999
COLUMN "8" FORMAT 9999999
COLUMN "9" FORMAT 9999999
COLUMN "10" FORMAT 9999999
column month format a13
COLUMN "RENTALS" FORMAT 999
COLUMN OUTLET_NUM FORMAT A13
COLUMN MAKES FORMAT A13
COLUMN SAME_STATERS FORMAT A10
COLUMN SAME_STATE_RENTALS FORMAT A20
COLUMN FNAME FORMAT A10
COLUMN LNAME FORMAT A15
COLUMN POSITION FORMAT A13
COLUMN EMPLOYEE FORMAT A50




COLUMN RENTALNO FORMAT A8
COLUMN LicenseNo FORMAT A10
COLUMN  "MILES_B" FORMAT 99999
COLUMN  "MILES_A" FORMAT 99999
COLUMN OutNo FORMAT A6
COLUMN MAKE FORMAT A10
COLUMN MODEL FORMAT A8
COLUMN YEAR FORMAT 9999
COLUMN Fault_Check FORMAT A11

1.)
SELECT RentalNo, TO_CHAR(StartDate, 'DD-MM-YY HH:MM:SS') AS "START", TO_CHAR(ReturnDate, 'DD-MM-YY HH:MM:SS') AS "RETURNED", LicenseNo, MileageBefore AS "MILES_B", MileageAfter AS "MILES_A", outNo,Make,Model,Year, DateChecked AS "Fault_Check"
FROM   RAGREEMENT
    JOIN VEHICLE USING (LicenseNo)
    LEFT OUTER JOIN FAULTREPORT USING (RentalNo,LicenseNo);

2.)

SELECT NVL(OutNo, ' Grand Total:') AS "OUTLET", COUNT(DISTINCT LicenseNo) AS "NUM_CARS", COUNT(DISTINCT RentalNo) AS "RENTALS_2017",
    ROUND(NVL(AVG(MileageAfter-MileageBefore),0),1) AS "AVG_DIST_2017", COUNT(DISTINCT EmpNo) AS "OUTLET_EMPLOYEES",
    ROUND(COUNT(DISTINCT RentalNo)/COUNT(DISTINCT EmpNo),1) AS "RENTALS_PER_EMP_2017"
FROM OUTLET
    JOIN VEHICLE USING (OutNo)
    JOIN EMPLOYEE USING (OutNo)
    LEFT OUTER JOIN (
        SELECT * 
        FROM RAGREEMENT 
        WHERE (StartDate >= to_date('01-01-2017','mm-dd-yyyy') AND  StartDate <=to_date('12-31-2017','mm-dd-yyyy')
            AND (ReturnDate >= to_date('01-01-2017','mm-dd-yyyy') AND  ReturnDate <=to_date('12-31-2017','mm-dd-yyyy'))
            )) USING (LicenseNo)
GROUP BY GROUPING SETS (OutNo,());


3.)

SELECT "Month1" AS Month,nvl("Outlet 1",0) "Outlet 1",nvl("Outlet 2",0) "Outlet 2",nvl("Outlet 3",0) "Outlet 3",nvl("Outlet 4",0) "Outlet 4",nvl("Outlet 5",0) "Outlet 5",nvl("Total_REV",0) "Total_Rev",nvl("RENTALS",0) "Rentals",nvl("REV/RENTAL",0) "Rev/Rental" from( select DISTINCT (CASE 
        WHEN to_char(ReturnDate,'MM') IS NULL THEN ' Grand Total:'
        ELSE to_char(ReturnDate,'MM') END) AS "Month",
    ROUND(sum(decode(OutNo,101,to_number(returndate-startdate)*DailyRate,0)),2) AS "Outlet 1",
    ROUND(sum(decode(OutNo,102,to_number(returndate-startdate)*DailyRate,0)),2) AS "Outlet 2",
    ROUND(sum(decode(OutNo,103,to_number(returndate-startdate)*DailyRate,0)),3) AS "Outlet 3",
    ROUND(sum(decode(OutNo,104,to_number(returndate-startdate)*DailyRate,0)),4) AS "Outlet 4",
    ROUND(sum(decode(OutNo,105,to_number(returndate-startdate)*DailyRate,0)),5) AS "Outlet 5",
    ROUND(sum((to_number(returndate-startdate)*DailyRate)),2) AS "Total_REV",
    count(DISTINCT RentalNo) AS "RENTALS",
    ROUND(sum((to_number(returndate-startdate)*DailyRate))/count(DISTINCT RentalNo),2) AS "REV/RENTAL"
FROM OUTLET
    JOIN VEHICLE USING (OutNo)
    JOIN RAGREEMENT USING (LicenseNo)
GROUP BY GROUPING SETS (to_char(ReturnDate,'MM'),())
) a right outer join (SELECT CASE WHEN month_value <10 THEN '0'||to_char(month_value) ELSE to_char(month_value) END AS "Month1" FROM WWV_FLOW_MONTHS_MONTH) b on "Month"="Month1"
ORDER BY "Month1" asc;
--to_char(b.month_value) ;


4.)

SELECT 
    (CASE 
        WHEN OutNo IS NULL THEN ' Grand Total:'
        ELSE OutNo
        END) AS OUTLET_NUM,
    (MON_S + MON_C) AS MON,
    (TUES_S + TUES_C) AS TUES,
    (WED_S + WED_C) AS WED,
    (THURS_S + THURS_C) AS THURS,
    (FRI_S + FRI_C) AS FRI,
    (SAT_S + SAT_C) AS SAT,
    (SUN_S + SUN_C) AS SUN,
    TOTAL_INITS
FROM(
SELECT outNo, 
    SUM(DECODE(REGEXP_SUBSTR(TO_CHAR(StartDate,'DAY'),'[A-Z]+'),NULL,0,1)) +
    SUM(DECODE(REGEXP_SUBSTR(TO_CHAR(DATECHECKED,'DAY'),'[A-Z]+'),NULL,0,1)) 
    AS TOTAL_INITS,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(StartDate,'DAY'),'[A-Z]+'),'MONDAY',1,0)) AS MON_S,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(StartDate,'DAY'),'[A-Z]+'),'TUESDAY',1,0)) AS TUES_S,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(StartDate,'DAY'),'[A-Z]+'),'WEDNESDAY',1,0)) AS WED_S,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(StartDate,'DAY'),'[A-Z]+'),'THURSDAY',1,0)) AS THURS_S,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(StartDate,'DAY'),'[A-Z]+'),'FRIDAY',1,0)) AS FRI_S,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(StartDate,'DAY'),'[A-Z]+'),'SATURDAY',1,0)) AS SAT_S,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(StartDate,'DAY'),'[A-Z]+'),'SUNDAY',1,0)) AS SUN_S,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(DATECHECKED,'DAY'),'[A-Z]+'),'MONDAY',1,0)) AS MON_C,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(DATECHECKED,'DAY'),'[A-Z]+'),'TUESDAY',1,0)) AS TUES_C,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(DATECHECKED,'DAY'),'[A-Z]+'),'WEDNESDAY',1,0)) AS WED_C,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(DATECHECKED,'DAY'),'[A-Z]+'),'THURSDAY',1,0)) AS THURS_C,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(DATECHECKED,'DAY'),'[A-Z]+'),'FRIDAY',1,0)) AS FRI_C,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(DATECHECKED,'DAY'),'[A-Z]+'),'SATURDAY',1,0)) AS SAT_C,
    sum(decode(REGEXP_SUBSTR(TO_CHAR(DATECHECKED,'DAY'),'[A-Z]+'),'SUNDAY',1,0)) AS SUN_C
FROM(
    SELECT OutNo, 
        (CASE
            WHEN MONTHS_BETWEEN(SYSDATE,DateChecked)<=6 THEN DateChecked
            ELSE NULL
            END) AS DateChecked,
        (CASE
            WHEN MONTHS_BETWEEN(SYSDATE,StartDate)<=6 THEN StartDate
            ELSE NULL
            END) AS StartDate
    FROM RAGREEMENT
        LEFT OUTER JOIN FAULTREPORT USING (RentalNo,LicenseNo)
        JOIN VEHICLE USING (LicenseNo)
        JOIN OUTLET USING (OutNo))
GROUP BY GROUPING SETS(OutNo,()));



5.)
SELECT 
(CASE
              WHEN OUTNO IS NULL THEN 'Total:'
              ELSE OUTNO 
              END) AS outno,
              empno,COUNT(DISTINCT RentalNo) AS "NO_RENTALS",
              sum(to_number(returndate-startdate)*DailyRate) as "Revenue",
sum(to_number(returndate-startdate)*DailyRate)/count(distinct rentalno) as "Rev/Rental",
COUNT(distinct ReportNum) AS "NUM_FAULTS"
FROM(SELECT managerno AS EmpNo, OutNo, LicenseNo, DailyRate
              FROM OUTLET 
              JOIN VEHICLE USING(OutNo))
              JOIN (SELECT EmpNo, FNAME,LNAME FROM EMPLOYEE) USING (EmpNo)
              LEFT OUTER JOIN RAGREEMENT USING(LicenseNo)
              LEFT OUTER JOIN (SELECT ReportNum,RentalNo FROM FAULTREPORT) USING(RentalNo)
GROUP By grouping sets ((outno, empno),empno)
order by OutNo;

6.)
SELECT outno, "Revenue" from (
SELECT outno, to_char(SUM ((ROUND((returndate - startdate),1) * vehicle.dailyrate)), '$99,999') AS "Revenue",rank() OVER (ORDER BY SUM ((ROUND((returndate - startdate),1) * vehicle.dailyrate))desc) rank from ragreement join vehicle using (licenseno) join outlet using (outno) 
where startdate>= '01-OCT-2017' and returndate <= '31-MAR-2018' group by outno ) where rank<=1
UNION 
SELECT outno, "Revenue" from (
SELECT outno, to_char(SUM ((ROUND((returndate - startdate),1) * vehicle.dailyrate)) , '$99,999')AS "Revenue",rank() OVER (ORDER BY SUM ((ROUND((returndate - startdate),1) * vehicle.dailyrate))asc) rank from ragreement join vehicle using (licenseno) join outlet using (outno) 
where startdate>= '01-OCT-2017' and returndate <= '31-MAR-2018' group by outno ) where rank<=1;

7.)
SELECT
    a.make,
    a.model,"# Cars","Avg Age",CASE WHEN "# Rentals this year" >0 THEN "# Rentals this year" ELSE 0 END AS "#Rentals 2018",CASE WHEN "Total # days rented">0 THEN "Total # days rented" ELSE 0 END AS "#Days rented", CASE when "# Fault reports" >0 THEN "# Fault reports" ELSE 0 END AS "Fault"
FROM
        (SELECT
            make,
            model,
            CASE
            WHEN COUNT(*)>0 THEN COUNT(*)
            ELSE 0 END "# Cars",
            CASE WHEN AVG(year) >0 THEN AVG(year) ELSE 0 END AS "Avg Age"
        FROM
            vehicle
            JOIN outlet USING ( outno )
        GROUP BY
            make,
            model) a  left outer join (SELECT make,model,
            CASE
            WHEN COUNT(*)>0 THEN COUNT(*)
            ELSE 0 END "# Rentals this year", CASE WHEN ROUND(SUM( returndate-startdate ),1) > 0 THEN  ROUND(SUM( returndate-startdate ),1) ELSE 0 END AS "Total # days rented"
        FROM
            ragreement
            JOIN vehicle USING ( licenseno )
        WHERE
            startdate >= '01-JAN-2018'
            AND startdate <= '31-DEC-2018'
        GROUP BY
            make,
            model) b on a.make=b.make and a.model=b.model   left outer join (select make,model,CASE WHEN count(*) >0 THEN COUNT(*) ELSE 0 END AS "# Fault reports" from faultreport join vehicle using (licenseno) group by make,model)    c on  b.make=b.make and b.model=c.model            
  UNION ALL
 SELECT
    a.make,
    'N.A',"# Cars","Avg Age",CASE WHEN "# Rentals this year" >0 THEN "# Rentals this year" ELSE 0 END AS "#Rentals 2018",CASE WHEN "Total # days rented">0 THEN "Total # days rented" ELSE 0 END AS "#Days rented", CASE when "# Fault reports" >0 THEN "# Fault reports" ELSE 0 END AS "Fault"
FROM
        (SELECT
            make,
            CASE
            WHEN COUNT(*)>0 THEN COUNT(*)
            ELSE 0 END "# Cars",
            CASE WHEN AVG(year) >0 THEN ROUND(AVG(year),1) ELSE 0 END AS "Avg Age"
        FROM
            vehicle
            JOIN outlet USING ( outno )
        GROUP BY
            make) a left outer join  (SELECT make,
            CASE
            WHEN COUNT(*)>0 THEN COUNT(*)
            ELSE 0 END "# Rentals this year", CASE WHEN ROUND(SUM( returndate-startdate ),1) > 0 THEN  ROUND(SUM( returndate-startdate ),1) ELSE 0 END AS "Total # days rented"
        FROM
            ragreement
            JOIN vehicle USING ( licenseno )
        WHERE
            startdate > '01-JAN-2018'
            AND startdate < '31-DEC-2018'
        GROUP BY
            make) b on a.make=b.make left outer join    (select make,CASE WHEN count(*) >0 THEN COUNT(*) ELSE 0 END AS "# Fault reports" from faultreport join vehicle using (licenseno) group by make) c on b.make=c.make            
UNION ALL
SELECT
    'Grand Total',
    'N.A',"# Cars","Avg Age",CASE WHEN "# Rentals this year" >0 THEN "# Rentals this year" ELSE 0 END AS "#Rentals 2018",CASE WHEN "Total # days rented">0 THEN "Total # days rented" ELSE 0 END AS "#Days rented", CASE when "# Fault reports" >0 THEN "# Fault reports" ELSE 0 END AS "Fault"
FROM
        (SELECT           
            CASE
            WHEN COUNT(*)>0 THEN COUNT(*)
            ELSE 0 END "# Cars",
            CASE WHEN AVG(year) >0 THEN ROUND(AVG(year),1) ELSE 0 END AS "Avg Age"
        FROM
            vehicle
            JOIN outlet USING ( outno )
       ) a  , (SELECT 
            CASE
            WHEN COUNT(*)>0 THEN COUNT(*)
            ELSE 0 END "# Rentals this year", CASE WHEN ROUND(SUM( returndate-startdate ),1) > 0 THEN  ROUND(SUM( returndate-startdate ),1) ELSE 0 END AS "Total # days rented"
        FROM
            ragreement
            JOIN vehicle USING ( licenseno )
        WHERE
            startdate >= '01-JAN-2018'
            AND startdate <= '31-DEC-2018'
       ) b , (select CASE WHEN count(*) >0 THEN COUNT(*) ELSE 0 END AS "# Fault reports" from faultreport join vehicle using (licenseno) where faultreport.datechecked >= '01-JAN-2018' and faultreport.datechecked<='31-DEC-2018')c;


8.)
select a.quarter,a.make,"# Fault Reports",CASE WHEN "COUNT(*)" IS NULL THEN 0 ELSE "COUNT(*)" END AS "# Rentals" from (select quarter,make,"# Fault Reports",RANK() OVER (PARTITION BY quarter
ORDER BY "# Fault Reports" DESC) "RANK" from (SELECT quarter,make,count(*)  as "# Fault Reports" from (SELECT
CASE
WHEN datechecked BETWEEN '01-JAN-2017' AND '31-MAR-2017' THEN 1
WHEN datechecked BETWEEN '01-APR-2017' AND '30-JUN-2017' THEN 2
WHEN datechecked BETWEEN '01-JUL-2017' AND '30-SEP-2017' THEN 3
WHEN datechecked BETWEEN '01-OCT-2017' AND '30-DEC-2017' THEN 4
END AS Quarter,make, reportnum from faultreport join vehicle using (licenseno) join ragreement using (rentalno)) group by quarter,make))a 
left outer join 
(select make,quarter,count(*)   from (
SELECT make,CASE
WHEN startdate BETWEEN '01-JAN-2017' AND '31-MAR-2017' THEN 1
WHEN startdate BETWEEN '01-APR-2017' AND '30-JUN-2017' THEN 2
WHEN startdate BETWEEN '01-JUL-2017' AND '30-SEP-2017' THEN 3
WHEN startdate BETWEEN '01-OCT-2017' AND '30-DEC-2017' THEN 4
END AS quarter from ragreement join vehicle using (licenseno) where startdate >= '01-JAN-2017' and startdate<='31-DEC-2017') group by make,quarter)b on a.quarter=b.quarter and a.make=b.make order by a.quarter asc;       

9.)
select a.OUTNO,"# Customers","No of bookings","Proportion","Proportion of rentals" from (select outno,count(distinct clientno) AS "# Customers" from ragreement join vehicle using (licenseno) join outlet o using (outno) join client c using (clientno) where o.state=c.state group by outno) a ,
(select outno, SUM("COUNT(*)") AS "No of bookings" from (select clientno,outno,count(*) from ragreement join vehicle using (licenseno) join outlet o using (outno) join client c using (clientno) where o.state=c.state group by outno,clientno) group by outno) b,(  select a.outno,ROUND(("1"/ ("1" + "2")),2) AS "Proportion" from ( select outno, count(distinct clientno) AS "1" from ragreement join vehicle using (licenseno) join outlet o using (outno) join client c using (clientno) where o.state=c.state group by outno) a,
(select outno, count(distinct clientno) AS "2" from ragreement join vehicle using (licenseno) join outlet o using (outno) join client c using (clientno) where o.state!=c.state group by outno) b where a.outno=b.outno    ) c, (  select a.outno,ROUND(("1"/ ("1" + "2")),2) AS "Proportion of rentals"   from (select outno, SUM("COUNT(*)") AS "1" from (select clientno,outno,count(*) from ragreement join vehicle using (licenseno) join outlet o using (outno) join client c using (clientno) where o.state=c.state group by outno,clientno) group by outno) a,
(select outno, SUM("COUNT(*)") AS "2" from (select clientno,outno,count(*) from ragreement join vehicle using (licenseno) join outlet o using (outno) join client c using (clientno) where o.state!=c.state group by outno,clientno) group by outno) b where a.outno=b.outno       ) d where a.outno=b.outno and a.outno=c.outno and a.outno=d.outno;

10.)
-- On me




7.) alternate: 

SELECT 
(CASE
    WHEN MAKE IS NULL THEN ' Grand Total:'
    ELSE MAKE
    END) AS MAKES,
MODEL, 
count(DISTINCT LicenseNo) AS "COUNT", 
AVG(YEAR) AVG_YEAR, 
SUM((CASE
    WHEN StartDate >= TO_DATE('01-JAN-2018','DD-MON-YYYY') AND StartDate <= TO_DATE('31-DEC-2018','DD-MON-YYYY') THEN returndate-startdate
    ELSE 0 END)) AS DAYS_RENTED_18, 
COUNT(DISTINCT(CASE
WHEN DATECHECKED >= TO_DATE('01-JAN-2018','DD-MON-YYYY') AND DATECHECKED <= TO_DATE('31-DEC-2018','DD-MON-YYYY') THEN ReportNum 
ELSE NULL END)) AS FAULT_REPORTS_18
FROM VEHICLE
    JOIN OUTLET USING (OUTNO)
    LEFT JOIN RAGREEMENT USING (LicenseNo)
    LEFT JOIN FAULTREPORT USING(RentalNo,LicenseNo)
GROUP BY GROUPING SETS((MAKE,MODEL),MAKE,());

