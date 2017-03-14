-- public.chemical
insert into public.chemical values(1, 'Ethylene', '乙烯', 28, 1.26,'C2H4','T', 593, 0, 'EUR', 1530);
insert into public.chemical values(2, 'Oxygen', '氧', 16, 1.4,'O2','T', 200, 0, 'EUR', 900);
insert into public.chemical values(3, 'Ethylene oxide', '环氧乙烷', 44, 0,'C2H4O','T', 800, 0, 'EUR', NULL);
insert into public.chemical values(4, 'carbon dioxide', '二氧化碳', 44, 0,'CO2','T', 40, 0, 'EUR', NULL);
insert into public.chemical values(5, 'water', '水', 18, 1,'H2O','T', 56, 0, 'EUR', NULL);
insert into public.chemical values(6, 'Ammonia', '氨', 18, 0,'NH3','T', 100, 0, 'EUR', NULL);
insert into public.chemical values(7, 'Ethanolamines', '单乙醇胺', 61, 0,'NH2CH2CH2OH','T', 1000, 0, 'EUR', NULL);
insert into public.chemical values(8, 'Di-Triethaolamines', '二-三乙醇胺', 115, 0,'DEA,TEA','T', 500, 0, 'EUR', NULL);

-- public.reaction_formula
insert into public.reaction_formula values(1, 'OPEX 环氧乙烷', 200, 20, '(-106.7-1327*(1/c-1))/3600');
insert into public.reaction_formula values(2, 'OPEX 乙醇胺', 200, 20, '-125/(c * 3600)');

-- public.reaction_product, the formula for quantity is based on the excel sheet
insert into public.reaction_product values(3, 1, '1', 'moles');
insert into public.reaction_product values(4, 1, '2*(1-c)/c', 'moles');
insert into public.reaction_product values(5, 1, '2*(1-c)/c', 'moles');
insert into public.reaction_product values(7, 2, '1', 'moles');
insert into public.reaction_product values(8, 2, '(62/c-61)/115', 'moles')


-- public.reaction_reactant (should be checked by the application since the conversion value can be changed)
-- or a database procedure
insert into public.reaction_reactant values(1, 1, '1/c', 'moles', -1);
insert into public.reaction_reactant values(2, 1, '1/c * c * 0.5 + 1/c * (1-c) * 3', 'moles', -1);
insert into public.reaction_reactant values(3, 2, '1/c', 'moles', 1);
insert into public.reaction_reactant values(6, 2, '1/c', 'moles', 1);

-- public.emission_data
insert into public.emission_data values(1, 1, 'CO2', '二氧化碳', 'kg/kg', 0.21, null, 0.22, 0.43);
insert into public.emission_data values(2, 1, 'PM particle', '细微颗粒', 'kg/kg', null, null, 0.0727, 0.0727);
insert into public.emission_data values(3, 1, 'NOx', '氮氧化物', 'kg/kg', null, null, 0.00748, 0.00748);
insert into public.emission_data values(4, 2, 'CO2', '二氧化碳', 'kg/kg', null, 0.16223021, 0.22, 0.38);
insert into public.emission_data values(5, 2, 'PM particle', '细微颗粒', 'kg/kg', null, 0.0226, 0.0727, 0.0953);
insert into public.emission_data values(6, 2, 'NOx', '氮氧化物', 'kg/kg', null, 0.00167, 0.00748, 0.00915);
insert into public.emission_data values(7, 2, 'NH3', '氨', 'kg/kg', null, null,null, 0.0587);
insert into public.emission_data values(8, 2, 'EO', '环氧乙烷', 'kg/kg', null, null, null, 0.0152);


-- gaolanport.factory_reaction_product
insert into gaolanport.factory_reaction_product values(2,1,3, 181898, 340,24,20,1,1,NULL, 'T', 0.86, 0.0216);
insert into gaolanport.factory_reaction_product values(2,2,7, 100000, 340,24,20,1,1,NULL, 'T', 0.70, 0.02);

-- gaolanport.utility_type
insert into gaolanport.utility_type values(1, 'electricity', '电力', 'KWh', '0.06', 'EUR');
insert into gaolanport.utility_type values(2, 'make up water', '补充水', 'Kg', '0.015', 'EUR');
insert into gaolanport.utility_type values(3, 'heat reaction', '化学反应热量', 'KWh', '0.02', 'EUR');
insert into gaolanport.utility_type values(4, 'heat thermal', '热量', 'KWh', '0.03', 'EUR');
insert into gaolanport.utility_type values(5, 'water treatment', '水处理', 'GJ', '0.35', 'EUR');

-- gaolanport.factory_reaction_utility
insert into gaolanport.factory_reaction_utility values()

-- gaolanport.factory_emission

-- gaolanport.factory (via QGIS)
insert into gaolanport.factory values(1, 'power plant', 'utility provider', '');
insert into gaolanport.factory values(2, 'BP factory', 'petrochemical', '');
insert into gaolanport.factory values(3, 'waste treament', 'utility provider', '');

-- change column type
-- alter table public.reaction_reactant alter column quantity type text using cast(quantity as text);