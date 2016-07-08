#!/bin/bash
# ---------------------------------------------------------
# Description: A fast tool for ElasticSearch.
# ---------------------------------------------------------

function help() {
	cat <<EOF
Usage: $0 <operation> [options]

Examples:
	$0 get demo-index
EOF
}

if [ $# -lt 1 ]; then
	help
	exit 1
fi

operation=$1
case $operation in
	get)
		echo "get"
		exit 0
		;;
	put)
		echo "put"
		exit 0
		;;
	delete)
		echo "delete"
		exit 0
		;;
	*)
		help
		exit 0
		;;
esac

