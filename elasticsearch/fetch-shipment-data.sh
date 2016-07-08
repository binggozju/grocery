#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
bin=${DIR}/../bin
lib=${DIR}/../lib

fetch_data_sql=$(cat <<EOF
SELECT
	spm.shipment_id as _id,

	spm.shipment_id as shipment_id,
	spm.created_user as created_user,	
	spm.created_time as created_time,
	spm.last_updated_time as last_updated_time,
	spm.last_updated_user as last_updated_user,
	spm.status as shipment_status,
	spm.shop_id as shop_id,
	spm.platform_id as platform_id,
	spm.merchant_id as merchant_id,
	spm.print_count as print_count,
	spm.shipping_self_weight as shipping_self_weight,
	spm.shipping_out_weight as shipping_out_weight,
	spm.shipping_service_fee as shipping_service_fee,
	spm.shipping_insured_cost as shipping_insured_cost,
	spm.estimated_shipping_fee as estimated_shipping_fee,
	spm.confirm_time as confirm_time,
	spm.schedule_time as schedule_time,
	spm.bind_time as bind_time,
	spm.create_batchpick_time as create_batchpick_time,
	spm.print_time as print_time,
	spm.shipping_time as shipping_time,
	spm.print_user_id as print_user_id,
	spm.ship_user_id as ship_user_id,
	spm.waybill_user_id as waybill_user_id,
	spm.waybill_time as waybill_time,
	spm.handle_time as handle_time,
	spm.goods_id as goods_id,
	spm.product_id as product_id,
	spm.product_name as product_name,
	spm.goods_number as goods_number,
	spm.order_type as order_type,
	spm.address_name as address_name,
	spm.order_status as order_status,
	spm.receive_name as receive_name,
	spm.mobile as mobile,
	spm.province_id as province_id,
	spm.province_name as province_name,
	spm.city_id as city_id,
	spm.city_name as city_name,
	spm.district_id as district_id,
	spm.district_name as district_name,
	spm.shipping_address as shipping_address,
	spm.secrect_code as secrect_code,
	spm.out_order_sn as out_order_sn,
	spm.order_sn_pad as order_sn_pad,
	spm.goods_name as goods_name,
	spm.send_oms_time as send_oms_time,
	spm.weight_user_id as weight_user_id,
	spm.weight_time as weight_time,
	spm.shipping_due_time as shipping_due_time,

	fcl.facility_id as facility_id,
	fcl.facility_name as facility_name,

	sp.shipping_id as shipping_id,
	sp.shipping_name as shipping_name,

	th.tracking_number as tracking_number,
	th.status as tracking_status,
	th.station_no as station_no,
	th.station as station,
	th.sender_branch_no as sender_branch_no,
	th.sender_branch as sender_branch

FROM
	ws_shipment spm
	LEFT JOIN ws_facility fcl ON spm.facility_id = fcl.facility_id
	LEFT JOIN ws_shipping sp ON spm.shipping_id = sp.shipping_id
	LEFT JOIN ws_thermal_express_mailnos th ON spm.shipment_id = th.shipment_id

WHERE
	unix_timestamp(spm.last_updated_time) > unix_timestamp(?)
OR
	unix_timestamp(th.last_update_time) > unix_timestamp(?)
EOF
)

function echo_config() {
echo "
{
    \"type\" : \"jdbc\",
    \"jdbc\" : {
        \"url\" : \"jdbc:mysql://columbu007tmstest.mysql.rds.aliyuncs.com/weishop\",
        \"statefile\" : \"statefile.json\",
        \"schedule\" : \"0 0/30 0-23 ? * *\",
        \"user\" : \"xxxxxx\",
        \"password\" : \"xxxxx\",
        \"sql\" : [{
				\"statement\": \"$*\",
				\"parameter\": [\"\$metrics.lastexecutionstart\", \"\$metrics.lastexecutionstart\"]}
            ],
        \"index\" : \"weishop_v1\",
        \"type\" : \"shipment\",
        \"metrics\": {
            \"enabled\" : true
        },
        \"elasticsearch\" : {
             \"cluster\" : \"es_in_testwms\",
             \"host\" : \"localhost\",
             \"port\" : 9300 
        }   
    }
}"
}

echo_config $fetch_data_sql | java \
    -cp "${lib}/*" \
    -Dlog4j.configurationFile=${bin}/log4j2.xml \
    org.xbib.tools.Runner \
    org.xbib.tools.JDBCImporter
