DROP FUNCTION IF EXISTS public.get_inventory_fsn_analysis_report_company_vise(integer[], integer[], integer[], integer[], date, date, text);
DROP FUNCTION IF EXISTS public.get_inventory_fsn_analysis_report_company_vise(integer[], integer[], integer[], integer[], date, date, text, integer);
CREATE OR REPLACE FUNCTION public.get_inventory_fsn_analysis_report_company_vise(
    IN company_ids integer[],
    IN product_ids integer[],
    IN category_ids integer[],
    IN warehouse_ids integer[],
    IN start_date date,
    IN end_date date,
    IN stock_movement_type text,
    IN fsn_wizard_id integer
)
RETURNS TABLE(
    company_id integer, company_name character varying,
    product_id integer, product_name character varying,
    product_category_id integer, category_name character varying,
    opening_stock numeric, closing_stock numeric,
    average_stock numeric, sales numeric,
    turnover_ratio numeric, stock_movement text
) AS
$BODY$
    BEGIN
--        Return Query
        DELETE FROM setu_inventory_fsn_analysis_bi_report;
        Insert into setu_inventory_fsn_analysis_bi_report(company_id,product_id,product_category_id,opening_stock,closing_stock,average_stock,sales,turnover_ratio,stock_movement,wizard_id)
        select F.company_id,F.product_id,F.product_category_id,
        F.opening_stock,F.closing_stock,F.average_stock,F.sales,F.turnover_ratio,F.stock_movement,fsn_wizard_id from(
        Select * From
        (
            Select
                t_data.*,
                case
                    when t_data.turnover_ratio > 3 then 'Fast Moving'
                    when t_data.turnover_ratio >= 1 and t_data.turnover_ratio <= 3 then 'Slow Moving'
                    when t_data.turnover_ratio < 1 then 'Non Moving'
                end as stock_movement
            From
            (
                Select * from setu_inventory_turnover_analysis_bi_report
            )t_data
        )report_data
        where
        1 = case when stock_movement_type = 'all' then 1
        else
            case when stock_movement_type = 'fast' then
                case when report_data.stock_movement = 'Fast Moving' then 1 else 0 end
            else
                case when stock_movement_type = 'slow' then
                    case when report_data.stock_movement = 'Slow Moving' then 1 else 0 end
                else
                    case when stock_movement_type = 'non' then
                        case when report_data.stock_movement = 'Non Moving' then 1 else 0 end
                    else 0 end

                end
            end
        end)F;
    END; $BODY$
LANGUAGE plpgsql VOLATILE
COST 100
ROWS 1000;
