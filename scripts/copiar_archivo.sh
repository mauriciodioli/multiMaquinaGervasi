#!/bin/bash
origen="$1"
destino="$2"

if [ ! -f "$origen" ]; then
  echo "❌ No se encuentra el archivo: $origen"
  exit 1
fi

mkdir -p "$destino"
cp "$origen" "$destino"
echo "✅ Copia realizada: $origen -> $destino"

