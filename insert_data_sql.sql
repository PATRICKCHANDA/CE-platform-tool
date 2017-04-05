-- public.chemical
insert into public.chemical values(1, 'Ethylene', '乙烯', 28, 1.26,'C2H4','T', 593, 0, 'EUR', 1530);
insert into public.chemical values(2, 'Oxygen', '氧', 32, 1.4,'O2','T', 200, 0, 'EUR', 900);
insert into public.chemical values(3, 'Ethylene oxide', '环氧乙烷', 44, 0,'C2H4O','T', 800, 0, 'EUR', NULL);
insert into public.chemical values(4, 'carbon dioxide', '二氧化碳', 44, 0,'CO2','T', 40, 0, 'EUR', NULL);
insert into public.chemical values(5, 'water', '水', 18, 1,'H2O','T', 56, 0, 'EUR', NULL);
insert into public.chemical values(6, 'Ammonia', '氨', 18, 0,'NH3','T', 100, 0, 'EUR', NULL);
insert into public.chemical values(7, 'Ethanolamines', '单乙醇胺', 61, 0,'NH2CH2CH2OH','T', 1000, 0, 'EUR', NULL);
insert into public.chemical values(8, 'Di-Triethaolamines', '二-三乙醇胺', 115, 0,'DEA,TEA','T', 500, 0, 'EUR', NULL);
insert into public.chemical values(9, 'p-xylene(PX)',       '对二甲苯', 106, 1.26, 'C8H10', 'T',593,0,'EUR',1530);
insert into public.chemical values(10, 'air',               '空气',    28.84, 1.4, '',        'T', 0, 0, 'EUR', 900);
insert into public.chemical values(11, 'Acetic acid',       '乙酸',    60,    0, 'CH3COOH', 'T', 300, 0, 'EUR', NULL);
insert into public.chemical values(12, 'normal water',      '普通水',   18,    0, 'H2O', 'T', 15, NULL, 'EUR', NULL);
insert into public.chemical values(13, 'Cobalt',            '钴',      59,    0, 'Co', 'T', 300, NULL, 'EUR', NULL);
insert into public.chemical values(14, 'Terepthalic acid(TA)',  '对苯二甲酸',166,   0, 'p-C6H4(COOH)2', 'T', 800, NULL, 'EUR', NULL);
insert into public.chemical values(15, 'Nitrogen',  '液氮', 14,   0, 'LN2', 'T', 200, NULL, 'EUR', NULL);

-- public.reaction_formula
insert into public.reaction_formula values(1, '环氧乙烷(EO)', 200, 20, '(-106.7-1327*(1/c-1))'); -- attention: do not divide by 3600, which is conversion from kJ to kWh
insert into public.reaction_formula values(2, '乙醇胺(MEA)', 200, 20, '-125/c');
insert into public.reaction_formula values(3, '对苯二甲酸(TA)', 150, 15, '-21200/c');
insert into public.reaction_formula values(4, '液化气体', 130, -192, '0');

-- public.reaction_product, the formula for quantity is based on the excel sheet
insert into public.reaction_product values(3, 1, '1', 'moles');
insert into public.reaction_product values(4, 1, '2*(1-c)/c', 'moles');
insert into public.reaction_product values(5, 1, '2*(1-c)/c', 'moles');
insert into public.reaction_product values(7, 2, '1', 'moles');
insert into public.reaction_product values(8, 2, '(62/c-61)/115', 'moles');
insert into public.reaction_product values(14, 3, '1', 'moles');
insert into public.reaction_product values(5, 3, '2/c', 'moles');
insert into public.reaction_product values(2, 4, '1', 'moles');
insert into public.reaction_product values(15, 4, '1.1', 'moles');


-- public.reaction_reactant (should be checked by the application since the conversion value can be changed)
-- or a database procedure
insert into public.reaction_reactant values(1, 1, '1/c', 'moles', -1, null);
insert into public.reaction_reactant values(2, 1, '1/c * c * 0.5 + 1/c * (1-c) * 3', 'moles', -1, null);
insert into public.reaction_reactant values(3, 2, '1/c', 'moles', 1, null);
insert into public.reaction_reactant values(6, 2, '1/c', 'moles', 1, null);
insert into public.reaction_reactant values(9, 3, '1/c', 'moles', -1, null);  -- p-xylene
insert into public.reaction_reactant values(10, 3, '1/(c * c * 0.21)', 'moles', -1, null); -- air
insert into public.reaction_reactant values(11, 3, '0.13833', 'moles', -1, true); -- acedic acid
insert into public.reaction_reactant values(12, 3, '4.15', 'moles', -1, true); -- normal water
insert into public.reaction_reactant values(13, 3, '0.140678', 'moles', -1, true); -- Co
insert into public.reaction_reactant values(10, 4, '1', 'moles', -1, null); -- air
-- select * from public.reaction_reactant;

-- public.emission_data
insert into public.emission_data values(1, 1, 'CO2', '二氧化碳', 'kg/kg', 0.21, null, 0.22, 0.43);
insert into public.emission_data values(2, 1, 'PM particle', '细微颗粒', 'kg/kg', null, null, 0.000727, 0.000727);
insert into public.emission_data values(3, 1, 'NOx', '氮氧化物', 'kg/kg', null, null, 0.0000748, 0.0000748);
insert into public.emission_data values(4, 2, 'CO2', '二氧化碳', 'kg/kg', null, 0.16223021, 0.22267, 0.38490);
insert into public.emission_data values(5, 2, 'PM particle', '细微颗粒', 'kg/kg', null, 0.000226, 0.000727, 0.000953);
insert into public.emission_data values(6, 2, 'NOx', '氮氧化物', 'kg/kg', null, 0.0000167, 0.0000748, 0.0000915);
insert into public.emission_data values(7, 2, 'NH3', '氨', 'kg/kg', null, null,null, 0.00587);
insert into public.emission_data values(8, 2, 'EO', '环氧乙烷', 'kg/kg', null, null, null, 0.00152);
insert into public.emission_data values(9, 3, 'PM particle', '细微颗粒', 'kg/kg', 0.0000612, 0.000184, 0.00103, 0.00128);
insert into public.emission_data values(10, 3, 'NOx', '氮氧化物', 'kg/kg', null, 0.0000136, 0.000106, 0.00012);
insert into public.emission_data values(11, 3, 'HC', '烃', 'kg/kg', null, null,null, 0.004);
insert into public.emission_data values(12, 3, 'CO2', '二氧化碳', 'kg/kg', null, 0.13221762, 0.32, 0.45);


-- gaolanport.factory_reaction_product
insert into gaolanport.factory_reaction_product values(2,1,3, 181898, 340,24,20,1,1,NULL, 'T', 0.86, 0.0216);
insert into gaolanport.factory_reaction_product values(2,2,7, 100000, 340,24,20,1,1,NULL, 'T', 0.70, 0.02);  
insert into gaolanport.factory_reaction_product values(4,3,14, 80000, 340,24,20,1,1,NULL, 'T', 0.95, 0.02);  -- TA
insert into gaolanport.factory_reaction_product values(5,4,15, 100000, 340,24,20,1,1,NULL, 'T', 0.99, NULL); -- N2
insert into gaolanport.factory_reaction_product values(5,4,2, 100000, 340,24,20,1,1,NULL, 'T', 0.99, NULL);  -- O2

select * from  gaolanport.factory_reaction_product;

-- gaolanport.utility_type
insert into gaolanport.utility_type values(1, 'electricity', '电力', 'KWh', '0.06', 'EUR');
insert into gaolanport.utility_type values(2, 'make up water', '补充水', 'Kg', '0.015', 'EUR');
insert into gaolanport.utility_type values(3, 'heat reaction', '化学反应热量', 'KWh', '0.02', 'EUR');
insert into gaolanport.utility_type values(4, 'heat thermal', '热量', 'KWh', '0.03', 'EUR');
insert into gaolanport.utility_type values(5, 'water treatment', '水处理', 'GJ', '0.35', 'EUR');

-- gaolanport.factory_reaction_utility
insert into gaolanport.factory_reaction_utility values(2,1,1,null,null,null);
insert into gaolanport.factory_reaction_utility values(2,1,2,null,null,null);
insert into gaolanport.factory_reaction_utility values(2,1,3,null,null,null);
insert into gaolanport.factory_reaction_utility values(2,1,4,null,null,null);
insert into gaolanport.factory_reaction_utility values(2,1,5,null,null,null);
insert into gaolanport.factory_reaction_utility values(4,3,1,null,null,null);
insert into gaolanport.factory_reaction_utility values(4,3,2,null,null,null);
insert into gaolanport.factory_reaction_utility values(4,3,3,null,null,null);
insert into gaolanport.factory_reaction_utility values(4,3,4,null,null,null);
insert into gaolanport.factory_reaction_utility values(4,3,5,null,null,null);
--select * from gaolanport.factory_reaction_utility;

-- gaolanport.factory_emission

-- gaolanport.factory (via QGIS)
insert into gaolanport.factory values(1, '钰海电力', 'infrastructure', '');
insert into gaolanport.factory values(2, 'factory 2', 'petrochemical', '');
insert into gaolanport.factory values(3, '水质净化厂', 'infrastructure', '');
insert into gaolanport.factory values(4, 'BP petrochem', 'infrastructure', '');
insert into gaolanport.factory values(5, '中海油工业气体（珠海）有限公司', 'chain', '');

-- change column type
-- alter table public.reaction_reactant alter column quantity type text using cast(quantity as text);