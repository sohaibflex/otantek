-- Function: public.get_products_outofstock_data(integer[], integer[], integer[], integer[], date, date, integer)

DROP FUNCTION IF EXISTS public.get_products_outofstock_data(integer[], integer[], integer[], integer[], date, date, integer);
DROP FUNCTION IF EXISTS public.get_products_outofstock_data(integer[], integer[], integer[], integer[], date, date, integer, integer);

CREATE OR REPLACE FUNCTION public.get_products_outofstock_data(
IN company_ids integer[],
IN product_ids integer[],
IN category_ids integer[],
IN warehouse_ids integer[],
IN start_date date,
IN end_date date,
IN advance_stock_days integer,
IN wizard_id integer)
RETURNS VOID AS
$BODY$
    BEGIN
        Drop Table if exists outofstock_transaction_table;
        CREATE TEMPORARY TABLE outofstock_transaction_table(
            company_id INT,
            company_name character varying,
            product_id INT,
            product_name character varying,
            product_category_id INT,
            category_name character varying,
            warehouse_id INT,
            warehouse_name character varying,
            qty_available Numeric DEFAULT 0,
            outgoing numeric DEFAULT 0,
            incoming Numeric DEFAULT 0,
            forecasted_stock Numeric DEFAULT 0,
            sales numeric DEFAULT 0,
            ads numeric DEFAULT 0,
            demanded_qty numeric,
            in_stock_days numeric,
            out_of_stock_days numeric,
            cost_price numeric,
            out_of_stock_ratio numeric,
            out_of_stock_qty numeric,
            out_of_stock_value numeric
        );

        Insert into outofstock_transaction_table
        Select stockout_data.*,
            round((stockout_data.out_of_stock_days / case when advance_stock_days = 0 then 1 else advance_stock_days end * 100)::numeric, 0) as out_of_stock_ratio,
            round(stockout_data.out_of_stock_days * stockout_data.ads,0) as out_of_stock_qty,
            stockout_data.out_of_stock_days * stockout_data.ads * stockout_data.cost_price as out_of_stock_value
        from
        (
            Select
                final_data.*,
                case when (advance_stock_days - final_data.in_stock_days) > 0 then (advance_stock_days - final_data.in_stock_days)
                else 0 end as out_of_stock_days,
                coalesce(ir_property.value_float,0) as cost_price
            From
            (
                Select
                    stock_data.* , coalesce(round(sales_data.sales,0),0) as sales, coalesce(sales_data.ads,0) as ads,
                    Round(coalesce(advance_stock_days * sales_data.ads,0),0) as demanded_qty,
        case when
            coalesce(Round((stock_data.forecasted_stock / case when sales_data.ads <= 0.0000 then 0.001 else sales_data.ads end)::numeric, 0),0) < 0 then 0
                    else
            coalesce(Round((stock_data.forecasted_stock / case when sales_data.ads <= 0.0000 then 0.001 else sales_data.ads end)::numeric, 0),0)
        end as in_stock_days
                From
                (
                    Select
            T.company_id, T.company_name, T.product_id , T.product_name , T.product_category_id, T.category_name ,
            T.warehouse_id, T.warehouse_name, T.qty_available, T.outgoing, T.incoming,
            case when T.forecasted_stock > 0 then T.forecasted_stock else 0 end as forecasted_stock
                    from get_products_forecasted_stock_data(company_ids, product_ids, category_ids, warehouse_ids)T
                )stock_data

                Left Join
                (
                    select *, Round(D1.sales / ((end_date - start_date) + 1),2) as ads
                    from get_sales_transaction_data(company_ids, product_ids, category_ids, warehouse_ids, start_date, end_date) D1
                )sales_data
                    on stock_data.product_id = sales_data.product_id and stock_data.warehouse_id = sales_data.warehouse_id
            )final_data
                Left Join ir_property on 'product.product,' || final_data.product_id = ir_property.res_id
                                and ir_property.name = 'standard_price' and ir_property.company_id = final_data.company_id
        )stockout_data;

        Insert into setu_inventory_outofstock_bi_report(product_id, product_category_id, warehouse_id, company_id, sales,ads, demanded_qty, qty_available, incoming, outgoing, forecasted_stock, out_of_stock_ratio, in_stock_days, out_of_stock_days, cost_price, out_of_stock_qty, out_of_stock_value, out_of_stock_qty_per, out_of_stock_value_per, turnover_ratio,stock_movement,company_name,product_name,category_name,warehouse_name,wizard_id)
        select
         F.product_id, F.product_category_id, F.warehouse_id, F.company_id, F.sales,
         F.ads, F.demanded_qty, F.qty_available, F.incoming, F.outgoing, F.forecasted_stock,
          F.out_of_stock_ratio, F.in_stock_days, F.out_of_stock_days, F.cost_price, F.out_of_stock_qty,
           F.out_of_stock_value, F.warehouse_stockout_qty as out_of_stock_qty_per, F.warehouse_stockout_value as out_of_stock_value_per, F.turnover_ratio,F.stock_movement,
           F.company_name,F.product_name,F.category_name,F.warehouse_name,wizard_id
         from
        (with all_data as (
            Select * from outofstock_transaction_table
        ),
        warehouse_wise_outofstock as(
            Select ott.warehouse_id, ott.company_id,
                sum(ott.out_of_stock_qty) as total_stockout_qty, sum(ott.out_of_stock_value) as total_stockout_value
            from outofstock_transaction_table ott
            group by ott.warehouse_id, ott.company_id
        ),
        fsn_analysis as(
            Select *
            from setu_inventory_fsn_analysis_bi_report
        )
        Select
            all_data.*,
            case when wwover.total_stockout_qty <= 0.00 then 0 else
                Round((all_data.out_of_stock_qty / wwover.total_stockout_qty * 100)::numeric,2)
            end as warehouse_stockout_qty ,
            case when wwover.total_stockout_value <= 0.00 then 0 else
                Round((all_data.out_of_stock_value / wwover.total_stockout_value * 100)::numeric,2)
            end as warehouse_stockout_value,
            case when fsn.turnover_ratio > 0 then fsn.turnover_ratio else 0 end as turnover_ratio,
            fsn.stock_movement
        from all_data
            Inner Join warehouse_wise_outofstock wwover on wwover.warehouse_id = all_data.warehouse_id
            Left Join fsn_analysis fsn on fsn.product_id = all_data.product_id and fsn.warehouse_id = all_data.warehouse_id)F;
    END; $BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
