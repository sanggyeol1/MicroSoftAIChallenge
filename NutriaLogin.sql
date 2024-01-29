--피해년도 전처리
SELECT * 
FROM DAMAGE 
WHERE YEAR BETWEEN 2013 AND 2022;

--영남 습지 전처리
SELECT *
FROM WETLAND
WHERE ADDRESS LIKE '%경상%'
    OR ADDRESS LIKE '%부산%'
    OR ADDRESS LIKE '%대구%'
    OR ADDRESS LIKE '%울산%';
    
SELECT  
    -- 위도(LA) 변환
    CASE 
        WHEN SUBSTR(latitude, 1, 1) = 'N' THEN
            CAST(SUBSTR(latitude, 2, INSTR(latitude, '°') - 2) AS DECIMAL(9,6)) + 
            CAST(SUBSTR(latitude, INSTR(latitude, '°') + 1, INSTR(latitude, '’') - INSTR(latitude, '°') - 1) AS DECIMAL(9,6)) / 60 + 
            CAST(SUBSTR(latitude, INSTR(latitude, '’') + 1, INSTR(latitude, '"') - INSTR(latitude, '’') - 1) AS DECIMAL(9,6)) / 3600 
        ELSE 
            -(CAST(SUBSTR(latitude, 2, INSTR(latitude, '°') - 2) AS DECIMAL(9,6)) + 
            CAST(SUBSTR(latitude, INSTR(latitude, '°') + 1, INSTR(latitude, '’') - INSTR(latitude, '°') - 1) AS DECIMAL(9,6)) / 60 + 
            CAST(SUBSTR(latitude, INSTR(latitude, '’') + 1, INSTR(latitude, '"') - INSTR(latitude, '’') - 1) AS DECIMAL(9,6)) / 3600)
    END AS DecimalLatitude,
    -- 경도(LO) 변환
    CASE 
        WHEN SUBSTR(longitude, 1, 1) = 'E' THEN
            CAST(SUBSTR(longitude, 2, INSTR(longitude, '°') - 2) AS DECIMAL(9,6)) + 
            CAST(SUBSTR(longitude, INSTR(longitude, '°') + 1, INSTR(longitude, '’') - INSTR(longitude, '°') - 1) AS DECIMAL(9,6)) / 60 + 
            CAST(SUBSTR(longitude, INSTR(longitude, '’') + 1, INSTR(longitude, '"') - INSTR(longitude, '’') - 1) AS DECIMAL(9,6)) / 3600 
        ELSE 
            -(CAST(SUBSTR(longitude, 2, INSTR(longitude, '°') - 2) AS DECIMAL(9,6)) + 
            CAST(SUBSTR(longitude, INSTR(longitude, '°') + 1, INSTR(longitude, '’') - INSTR(longitude, '°') - 1) AS DECIMAL(9,6)) / 60 + 
            CAST(SUBSTR(longitude, INSTR(longitude, '’') + 1, INSTR(longitude, '"') - INSTR(longitude, '’') - 1) AS DECIMAL(9,6)) / 3600)
    END AS DecimalLongitude
FROM 
    wetland;
