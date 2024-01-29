--���س⵵ ��ó��
SELECT * 
FROM DAMAGE 
WHERE YEAR BETWEEN 2013 AND 2022;

--���� ���� ��ó��
SELECT *
FROM WETLAND
WHERE ADDRESS LIKE '%���%'
    OR ADDRESS LIKE '%�λ�%'
    OR ADDRESS LIKE '%�뱸%'
    OR ADDRESS LIKE '%���%';
    
SELECT  
    -- ����(LA) ��ȯ
    CASE 
        WHEN SUBSTR(latitude, 1, 1) = 'N' THEN
            CAST(SUBSTR(latitude, 2, INSTR(latitude, '��') - 2) AS DECIMAL(9,6)) + 
            CAST(SUBSTR(latitude, INSTR(latitude, '��') + 1, INSTR(latitude, '��') - INSTR(latitude, '��') - 1) AS DECIMAL(9,6)) / 60 + 
            CAST(SUBSTR(latitude, INSTR(latitude, '��') + 1, INSTR(latitude, '"') - INSTR(latitude, '��') - 1) AS DECIMAL(9,6)) / 3600 
        ELSE 
            -(CAST(SUBSTR(latitude, 2, INSTR(latitude, '��') - 2) AS DECIMAL(9,6)) + 
            CAST(SUBSTR(latitude, INSTR(latitude, '��') + 1, INSTR(latitude, '��') - INSTR(latitude, '��') - 1) AS DECIMAL(9,6)) / 60 + 
            CAST(SUBSTR(latitude, INSTR(latitude, '��') + 1, INSTR(latitude, '"') - INSTR(latitude, '��') - 1) AS DECIMAL(9,6)) / 3600)
    END AS DecimalLatitude,
    -- �浵(LO) ��ȯ
    CASE 
        WHEN SUBSTR(longitude, 1, 1) = 'E' THEN
            CAST(SUBSTR(longitude, 2, INSTR(longitude, '��') - 2) AS DECIMAL(9,6)) + 
            CAST(SUBSTR(longitude, INSTR(longitude, '��') + 1, INSTR(longitude, '��') - INSTR(longitude, '��') - 1) AS DECIMAL(9,6)) / 60 + 
            CAST(SUBSTR(longitude, INSTR(longitude, '��') + 1, INSTR(longitude, '"') - INSTR(longitude, '��') - 1) AS DECIMAL(9,6)) / 3600 
        ELSE 
            -(CAST(SUBSTR(longitude, 2, INSTR(longitude, '��') - 2) AS DECIMAL(9,6)) + 
            CAST(SUBSTR(longitude, INSTR(longitude, '��') + 1, INSTR(longitude, '��') - INSTR(longitude, '��') - 1) AS DECIMAL(9,6)) / 60 + 
            CAST(SUBSTR(longitude, INSTR(longitude, '��') + 1, INSTR(longitude, '"') - INSTR(longitude, '��') - 1) AS DECIMAL(9,6)) / 3600)
    END AS DecimalLongitude
FROM 
    wetland;
