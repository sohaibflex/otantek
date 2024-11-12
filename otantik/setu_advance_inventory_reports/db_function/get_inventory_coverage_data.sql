DROP FUNCTION IF EXISTS public.get_inventory_coverage_data(integer[], integer[], integer[], integer[], date, date, character varying,integer, character varying);
CREATE OR REPLACE FUNCTION public.get_inventory_coverage_data(
    IN company_ids integer[],
    IN product_ids integer[],
    IN category_ids integer[],
    IN warehouse_ids integer[],
    IN start_date date,
    IN end_date date,
    IN report_by character varying,
    IN wizard_id integer,
    IN include_internal_transfers character varying)
  RETURNS TABLE(company_id integer,product_id integer, product_category_id integer,warehouse_id integer,current_stock numeric,ads numeric,coverage_days numeric) AS
$BODY$
    DECLARE
        day_difference integer := ((end_date::Date-start_date::Date)+1);
    BEGIN
        DELETE FROM setu_inventory_coverage_analysis_bi_report;
        Insert into setu_inventory_coverage_analysis_bi_report(company_id,company_name,product_id,product_name,product_category_id,category_name,warehouse_id,warehouse_name,current_stock,average_daily_sales,coverage_days,wizard_id)
        select
            cov.company_id,
            cov.company_name,
            cov.product_id,
            cov.product_name,
            cov.product_category_id,
            cov.category_name,
            case when report_by='warehouse' then cov.warehouse_id
            else 1 end as warehouse_id,
            case when report_by='warehouse' then cov.warehouse_name
            else 'company' end as warehouse_name,
            sum(cov.current_stock) as current_stock,
            case when sum(cov.sales) > 0 then round(sum(cov.sales) /day_difference,2)
            else 0 end as ads,
            case when sum(cov.sales) > 0 and sum(cov.current_stock) > 0 and round(sum(cov.sales) /day_difference,2) > 0 then round(sum(cov.current_stock)/round(sum(cov.sales) /day_difference,2))
            else 0 end as coverage_days,
            wizard_id
        from
            (
            select S.company_id,cmp.name as company_name, S.product_id,
             case when prod.default_code is not null then
                ('['||prod.default_code||']'||' '||tmpl.name) else tmpl.name end as product_name,
             S.product_category_id,cat.complete_name as category_name,S.warehouse_id,ware.name as warehouse_name, sum(S.current_stock) as current_stock,0 as sales
                from get_current_stock_data(company_ids, product_ids, category_ids, warehouse_ids, start_date, end_date)S
                Inner Join res_company cmp on cmp.id = S.company_id
                Inner Join product_product prod on prod.id = S.product_id
                Inner Join product_template tmpl on tmpl.id = prod.product_tmpl_id
                Inner Join product_category cat on cat.id = tmpl.categ_id
                Inner Join stock_warehouse ware on ware.id = S.warehouse_id
                group by 1,2,3,4,5,6,7,8

            union all
            select T.company_id,T.company_name,T.product_id,T.product_name,T.product_category_id,T.category_name,T.warehouse_id,T.warehouse_name, 0 as current_stock,T.sales_qty as sales
                from get_sales_production_transaction_data(company_ids, product_ids, category_ids, warehouse_ids, start_date, end_date,include_internal_transfers)T
            )cov

            group by 1,2,3,4,5,6,7,8;
    END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100
ROWS 1000;
