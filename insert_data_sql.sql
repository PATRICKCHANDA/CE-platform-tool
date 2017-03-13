-- public.chemical
insert into public.chemical values(1, 'Ethylene', '““œ©', 28, 1.26,'C2H4','T', 593, 0, 'value in EUR');
insert into public.chemical values(2, 'Oxygen', '—ı', 16, 1.4,'O2','T', 200, 0, 'value in EUR');
insert into public.chemical values(3, 'Ethylene oxide', 'ª∑—ı““ÕÈ', 44, 0,'C2H4O','T', 800, 0, 'value in EUR');
insert into public.chemical values(4, 'carbon dioxide', '∂˛—ıªØÃº', 44, 0,'CO2','T', 40, 0, 'recycle or treatment cost in EUR');
insert into public.chemical values(5, 'water', 'ÀÆ', 18, 1,'H2O','T', 56, 0, 'recycle or treatment cost in EUR');

-- public.reaction_formula
insert into public.reaction_formula values(1, 'OPEX ª∑—ı““ÕÈ', 200, 20);

-- public.reaction_product, the formula for quantity is based on the excel sheet
insert into public.reaction_product values(3, 1, 1, 'moles');
insert into public.reaction_product values(4, 1, '2*(1-c)/c', 'moles');
insert into public.reaction_product values(5, 1, '2*(1-c)/c', 'moles');

-- public.reaction_reactant (should be checked by the application since the conversion value can be changed)
-- or a database procedure
insert into public.reaction_reactant values(1, 1, '1/c', 'moles', -1);
insert into public.reaction_reactant values(2, 1, '1/c * c * 0.5 + 1/c * (1-c) * 3', 'moles', -1);


-- gaolanport.factory_reaction_product
insert into gaolanport.factory_reaction_product values(2,1,3, 181898, 340,24,20,1,1,NULL, 'T', 0.86);

-- gaolanport.factory (via QGIS)
insert into gaolanport.factory values(1, '', , '');

-- change column type
-- alter table public.reaction_reactant alter column quantity type text using cast(quantity as text);