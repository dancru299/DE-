#!/usr/bin/env bash
# Dựng lại database từ đầu rồi mở shell DuckDB.
#   ./chay.sh          -> dựng lại sạch rồi vào shell
#   ./chay.sh giu      -> giữ nguyên database hiện có, chỉ mở shell
set -euo pipefail
cd "$(dirname "$0")"

if [ "${1:-}" != "giu" ]; then
  rm -f de.duckdb de.duckdb.wal
  duckdb de.duckdb < seed.sql
  echo
  echo "Database đã dựng lại từ đầu: de.duckdb"
fi

echo "Gõ .tables để xem bảng, .quit để thoát."
echo
exec duckdb de.duckdb
