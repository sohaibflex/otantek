DROP FUNCTION IF EXISTS public.get_stock_data_closing(integer[], integer[], integer[], integer[], date, date);
CREATE OR REPLACE FUNCTION public.get_stock_data_closing(
    IN company_ids integer[],
    IN product_ids integer[],
    IN category_ids integer[],
    IN warehouse_ids integer[],
    IN start_date date,
    IN end_date date)
  RETURNS TABLE(company_id integer, company_name character varying, product_id integer, product_name character varying, product_category_id integer, category_name character varying, warehouse_id integer, warehouse_name character varying, product_qty numeric) AS
$BODY$
DECLARE
    tr_start_date timestamp without time zone := (start_date || ' 00:00:00')::timestamp without time zone;
    tr_end_date timestamp without time zone:= (end_date || ' 23:59:59')::timestamp without time zone;
    products INT[];
BEGIN
    IF array_length(category_ids, 1) is not null and array_length(product_ids, 1) is null then
            products := (select array(select prod.id from product_category cat
            join product_template tmpl on tmpl.categ_id = cat.id
            join product_product prod on prod.product_tmpl_id = tmpl.id
            --category dynamic condition
            and 1 = case when array_length(category_ids,1) >= 1 then
                case when tmpl.categ_id = ANY(category_ids) then 1 else 0 end
                else 1 end));
            product_ids := products;
        END IF;
    RETURN QUERY
    with ware_location as (
        select
            sw.id as warehouse_id,
            sl.id as location_id
        from stock_warehouse sw
        join stock_location sl
        on
            sl.parent_path::text ~~ concat('%/', sw.view_location_id, '/%')
        where sl.usage not in ('view')
        --company dynamic condition
        and 1 = case when array_length(company_ids,1) >= 1 then
            case when sw.company_id = ANY(company_ids) then 1 else 0 end
            else 1 end
        --company dynamic condition
        and 1 = case when array_length(warehouse_ids,1) >= 1 then
            case when sw.id = ANY(warehouse_ids) then 1 else 0 end
            else 1 end
    )

    select
        tmp.company_id,
		cmp.name as company_name,
        tmp.product_id,
		case when prod.default_code is not null then
                ('['||prod.default_code||']'||' '||tmpl.name) else tmpl.name end as product_name,
		tmpl.categ_id as category_id,
		cat.complete_name as category_name,
        wh.warehouse_id as warehouse_id,
		sw.name as warehouse_name,
        case when sum(qty) >=0 then sum(qty) else 0 end as product_qty
        from(

            select
                COALESCE(sm.company_id,t.company_id) as company_id,
                COALESCE(sm.product_id, t.product_id) as product_id,
                COALESCE(sm.location_id,t.location_dest_id) as location_id,
                COALESCE((COALESCE(t.qty_in, 0) - COALESCE(sm.qty_out, 0)),0)  as qty
            from (
                    select
                        sm.company_id,
                        sm.product_id,
                        sm.location_id,
                        sum(sm.product_uom_qty) as qty_out
                    from
                        stock_move sm
                        Inner Join stock_location source on source.id = sm.location_id
                        Inner Join stock_location dest on dest.id = sm.location_dest_id
                        Left Join stock_warehouse source_warehouse ON source.parent_path::text ~~ concat('%/', source_warehouse.view_location_id, '/%')
                        Left Join stock_warehouse dest_warehouse ON dest.parent_path::text ~~ concat('%/', dest_warehouse.view_location_id, '/%')
                    where
                        sm.state='done'
                        and sm.date::date >= tr_start_date and sm.date::date <= tr_end_date
                        and sm.location_id in (select location_id from ware_location)
                        --product dynamic condition
                        and 1 = case when array_length(product_ids,1) >= 1 then
                            case when sm.product_id = ANY(product_ids) then 1 else 0 end
                            else 1 end
                        and 1 = case when dest.usage = 'internal' then
                			case when
                                            (source_warehouse.company_id = dest_warehouse.company_id
                                            and source_warehouse.id != dest_warehouse.id) then 1 else 0 end
                                        else 1 end
                    group by
                        sm.company_id, sm.product_id, sm.location_id)sm

            full join (
            select
                    sm.company_id,
                    sm.product_id,
                    sm.location_dest_id,
                    sum(sm.product_uom_qty) as qty_in
            from
                stock_move sm
                Inner Join stock_location source on source.id = sm.location_id
                Inner Join stock_location dest on dest.id = sm.location_dest_id
                Left Join stock_warehouse source_warehouse ON source.parent_path::text ~~ concat('%/', source_warehouse.view_location_id, '/%')
                Left Join stock_warehouse dest_warehouse ON dest.parent_path::text ~~ concat('%/', dest_warehouse.view_location_id, '/%')
            where
                sm.state='done'
                and sm.date::date >= tr_start_date and sm.date::date <= tr_end_date
                and sm.location_dest_id in (select location_id from ware_location)
                --product dynamic condition
                and 1 = case when array_length(product_ids,1) >= 1 then
                    case when sm.product_id = ANY(product_ids) then 1 else 0 end
                    else 1 end
                and 1 = case when source.usage = 'internal' then
                			case when
                                            (source_warehouse.company_id = dest_warehouse.company_id
                                            and source_warehouse.id != dest_warehouse.id) then 1 else 0 end
                                        else 1 end
            group by
                sm.company_id, sm.product_id, sm.location_dest_id
            order by 1,2)t
            on t.product_id = sm.product_id and t.location_dest_id = sm.location_id
          )tmp
    join (
        select * from ware_location
    )wh on tmp.location_id=wh.location_id
    join product_product prod on prod.id = tmp.product_id
	join product_template tmpl on tmpl.id = prod.product_tmpl_id
	join product_category cat on cat.id = tmpl.categ_id
	join res_company cmp on cmp.id = tmp.company_id
	join stock_warehouse sw on sw.id = wh.warehouse_id
	where prod.active = true and tmpl.active = true
	and tmpl.type = 'product'
    group by tmp.company_id, tmp.product_id, tmpl.categ_id, wh.warehouse_id, cmp.name, prod.default_code, tmpl.name, cat.complete_name, sw.name;
END; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
