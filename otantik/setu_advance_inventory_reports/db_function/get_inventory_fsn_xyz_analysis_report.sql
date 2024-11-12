DROP FUNCTION IF EXISTS public.get_inventory_fsn_xyz_analysis_report(integer[], integer[], integer[], integer[], date, date, text, text);
DROP FUNCTION IF EXISTS public.get_inventory_fsn_xyz_analysis_report(integer[], integer[], integer[], integer[], date, date, text, text,integer);
CREATE OR REPLACE FUNCTION public.get_inventory_fsn_xyz_analysis_report(
    IN company_ids integer[],
    IN product_ids integer[],
    IN category_ids integer[],
    IN warehouse_ids integer[],
    IN start_date date,
    IN end_date date,
    IN stock_movement_type text,
    IN stock_value_type text,
    IN fsn_xyz_wizard_id integer)
--RETURNS TABLE(company_id integer, company_name character varying, product_id integer, product_name character varying, product_category_id integer, category_name character varying, average_stock numeric, sales numeric, turnover_ratio numeric, fsn_classification text, current_stock numeric, stock_value numeric, xyz_classification text, combine_classification text) AS
RETURNS VOID AS
$BODY$
    BEGIN
        DELETE FROM setu_inventory_fsn_xyz_analysis_bi_report;
        Insert into setu_inventory_fsn_xyz_analysis_bi_report(company_id,product_id,product_category_id,average_stock,sales,turnover_ratio,fsn_classification,current_stock,stock_value,xyz_classification,combine_classification,company_name,product_name,category_name,wizard_id)
        select F.company_id,F.product_id,F.product_category_id,F.average_stock,F.sales,F.turnover_ratio,F.fsn_classification,F.current_stock,F.stock_value,F.xyz_classification,F.combine_classification,F.company_name,F.product_name,F.category_name,fsn_xyz_wizard_id
        from(
        Select
            xyz.company_id,xyz.product_id, xyz.product_category_id,fsn.average_stock, fsn.sales, fsn.turnover_ratio, fsn.stock_movement as fsn_classification,
            xyz.current_stock, xyz.stock_value, xyz.analysis_category as xyz_classification,
            ((case
                when fsn.stock_movement = 'Fast Moving' then 'F'
                when fsn.stock_movement = 'Slow Moving' then 'S'
                when fsn.stock_movement = 'Non Moving' then 'N'
            end) ||  xyz.analysis_category)::text as combine_classification,
            xyz.company_name,xyz.product_name,xyz.category_name

        from
        ( select * from setu_inventory_xyz_analysis_bi_report
        ) xyz
            Inner Join
        (select * from setu_inventory_fsn_analysis_bi_report
        ) fsn
            on xyz.product_id = fsn.product_id and xyz.company_id = fsn.company_id
        order by xyz.stock_value desc)F;
    END; $BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
