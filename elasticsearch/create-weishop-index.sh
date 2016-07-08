#!/bin/bash
# ----------------------------------------------------------------------------------
# Description: Create the index of weishop in ElasticSearch. Some fields the value 
#	of which is chinese should use elasticsearch-analysis-ik. Here are the steps:
# Usage: 
# - create_weishop-index.sh, create a index if and only if the given index does not exist.
# - create_weishop-index.sh force, create a index whether the given index exists or not.
# ----------------------------------------------------------------------------------

if [ $# -eq 1 ] && [ $1 = force ]; then
	FORCE=yes
fi

INDEX=weishop_v1
INDEX_ALIAS=weishop
TYPE=shipment
ES_HOSTS=http://localhost:9200
SHARDS_NUM=6
REPLICAS_NUM=1

function check_index_exist() {
	local index=$1
	local status_code=$(eval curl -XHEAD -i '$ES_HOSTS/$index' 2> /dev/null | head -1 | cut -d' ' -f2)
	if [ $status_code -eq 200 ]; then
		echo "1"	# exist
	else
		echo "0"	# not exist
	fi
}

# update the index_settings according to your needs.
index_settings=$(cat <<EOF
{
"aliases": {
	"$INDEX_ALIAS": {}
},
"settings": {
	"number_of_shards": $SHARDS_NUM,
	"number_of_replicas": $REPLICAS_NUM
},
"mappings": {
	"$TYPE": {
		"properties": {
			"shipment_id": {
				"type": "long"
			},
			"created_user": {
				"type": "string",
				"index": "not_analyzed"
			},
			"created_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"last_updated_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"last_updated_user": {
				"type": "string",
				"index": "not_analyzed"
			},
			"shipment_status": {
				"type": "string",
				"index": "not_analyzed"
			},
			"shop_id": {
				"type": "long"
			},
			"platform_id": {
				"type": "long"
			},
			"merchant_id": {
				"type": "long"
			},
			"print_count": {
				"type": "long"
			},
			"shipping_self_weight": {
				"type": "double"
			},
			"shipping_out_weight": {
				"type": "double"
			},
			"shipping_service_fee": {
				"type": "double"
			},
			"shipping_insured_cost": {
				"type": "double"
			},
			"estimated_shipping_fee": {
				"type": "double"
			},
			"confirm_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"schedule_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"bind_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"create_batchpick_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"print_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"shipping_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"print_user_id": {
				"type": "long"
			},
			"ship_user_id": {
				"type": "long"
			},
			"waybill_user_id": {
				"type": "long"
			},
			"waybill_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"handle_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"goods_id": {
				"type": "long"
			},
			"product_id": {
				"type": "long"
			},
			"product_name": {
				"type": "string",
				"analyzer": "ik_max_word",
				"search_analyzer": "ik_max_word"
			},
			"goods_number": {
				"type": "long"
			},
			"order_type": {
				"type": "long"
			},
			"address_name": {
				"type": "string",
				"analyzer": "ik_max_word",
				"search_analyzer": "ik_max_word"
			},
			"order_status": {
				"type": "long"
			},
			"receive_name": {
				"type": "string",
				"index": "not_analyzed"
			},
			"mobile": {
				"type": "string",
				"index": "not_analyzed"
			},
			"province_id": {
				"type": "long"
			},
			"province_name": {
				"type": "string",
				"index": "not_analyzed"
			},
			"city_id": {
				"type": "long"
			},
			"city_name": {
				"type": "string",
				"index": "not_analyzed"
			},
			"district_id": {
				"type": "long"
			},
			"district_name": {
				"type": "string",
				"index": "not_analyzed"
			},
			"shipping_address": {
				"type": "string",
				"analyzer": "ik_max_word",
				"search_analyzer": "ik_max_word"
			},
			"secrect_code": {
				"type": "string",
				"index": "not_analyzed"
			},
			"out_order_sn": {
				"type": "string",
				"index": "not_analyzed"
			},
			"order_sn_pad": {
				"type": "long"
			},
			"goods_name": {
				"type": "string",
				"analyzer": "ik_max_word",
				"search_analyzer": "ik_max_word"
			},
			"send_oms_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"weight_user_id": {
				"type": "long"		
			},
			"weight_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"shipping_due_time": {
				"type": "date",
				"format": "strict_date_optional_time||epoch_millis"
			},
			"facility_id": {
				"type": "long"
			},
			"facility_name": {
				"type": "string",
				"index": "not_analyzed"
			},
			"shipping_id": {
				"type": "long"
			},
			"shipping_name": {
				"type": "string",
				"index": "not_analyzed"
			},
			"tracking_number": {
				"type": "string",
				"index": "not_analyzed"
			},
			"tracking_status": {
				"type": "string",
				"index": "not_analyzed"
			},
			"station_no": {
				"type": "string",
				"index": "not_analyzed"
			},
			"station": {
				"type": "string",
				"index": "not_analyzed"
			},
			"sender_branch_no": {
				"type": "string",
				"index": "not_analyzed"
			},
			"sender_branch": {
				"type": "string",
				"index": "not_analyzed"
			}

		}
	}
}
}
EOF
)

function create_weishop_index() {
	curl -XPUT "$ES_HOSTS/$INDEX/" -d "$index_settings" 2> /dev/null
}

exist=`check_index_exist $INDEX`
if [ $exist -eq 1 ]; then
	if [ -n "$FORCE" ]; then
		echo "index '$INDEX' already exist, delete it"
		curl -XDELETE "$ES_HOSTS/$INDEX" 2> /dev/null
		echo "create index '$INDEX'"
		create_weishop_index
	else
		echo "index '$INDEX' already exist, quit"
		exit 1
	fi
else
	echo "create index '$INDEX'"
	create_weishop_index
fi

